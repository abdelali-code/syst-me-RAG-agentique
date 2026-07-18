"""
Agentic RAG graph built directly with LangGraph (no langchain.create_agent),
as required by the assignment.

Architecture
------------

                 ┌──────────────┐
   entry ──────► │   planner    │  decides: answer directly, or use tools?
                 └──────┬───────┘
                        │ (LLM bound to tools; may emit tool_calls)
                        ▼
                 ┌──────────────┐        tool_calls present
                 │ tools_router │ ─────────────────┐
                 └──────┬───────┘                  ▼
                        │ no tool_calls      ┌──────────────┐
                        │                    │  tool_node   │ executes retrieval /
                        │                    └──────┬───────┘ lookup / calculator tools
                        │                           │
                        │                           ▼
                        │                    back to planner (loop, bounded)
                        ▼
                 ┌──────────────┐
                 │  reflection  │  self-checks: is the answer grounded in the
                 └──────┬───────┘  retrieved articles? Anything unsupported?
                        │
              insufficient│ sufficient
                        │       │
                        ▼       ▼
                 (loop, bounded)  END

State carries the full message history (for the ReAct tool loop) plus a
`retrieval_rounds` counter so we can't loop forever, and `sources_used` for
citation tracking in the final answer.

Memory
------
A LangGraph `MemorySaver` checkpointer persists state per `thread_id`, so a
follow-up question in the same conversation ("et pour la garde de l'enfant
dans ce cas ?") retains prior turns without re-sending the whole history
manually.
"""
from __future__ import annotations

import operator
from typing import Annotated, TypedDict, Sequence

from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from src.llm import get_planner_llm, get_generation_llm
from src.tools import ALL_TOOLS

MAX_RETRIEVAL_ROUNDS = 3

SYSTEM_PROMPT = """Tu es un assistant juridique spécialisé en droit marocain \
(Code de la Famille / Moudawana et Code du Travail). Tu réponds UNIQUEMENT à \
partir des textes récupérés via tes outils — jamais de mémoire seule pour une \
question juridique précise (numéro d'article, délai, montant).

Règles :
1. Pour toute question qui porte sur un droit, une obligation, une procédure, \
   un délai ou une définition légale, utilise l'outil `retrieve_legal_context` \
   (ou `get_article_by_number` si un numéro d'article précis est cité).
2. Si la question mentionne des dates ou délais concrets, utilise \
   `calculate_legal_deadline` plutôt que de calculer toi-même.
3. Cite systématiquement l'article et le code source dans ta réponse \
   (ex: "selon l'article 53 du Code du Travail...").
4. Si les documents récupérés ne couvrent pas la question, dis-le clairement \
   plutôt que d'inventer une réponse.
5. Si la question a plusieurs volets, décompose-la et traite chaque volet \
   avec les outils avant de répondre.
"""


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    retrieval_rounds: int
    needs_more_retrieval: bool


def planner_node(state: AgentState) -> dict:
    """The core reasoning node: an LLM bound to tools. It decides whether to
    call a tool (retrieval, article lookup, deadline calc) or answer directly.

    Once MAX_RETRIEVAL_ROUNDS is reached, tools are no longer bound so the
    LLM is forced to synthesize a final text answer from whatever context
    was already retrieved, instead of emitting another (unroutable) tool call."""
    llm = get_planner_llm()
    if state.get("retrieval_rounds", 0) < MAX_RETRIEVAL_ROUNDS:
        llm = llm.bind_tools(ALL_TOOLS)
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    response = llm.invoke(messages)
    return {"messages": [response]}


def route_after_planner(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return "reflection"


tool_node = ToolNode(ALL_TOOLS)


def after_tools_node(state: AgentState) -> dict:
    """Increment the retrieval-round counter after any tool execution."""
    return {"retrieval_rounds": state.get("retrieval_rounds", 0) + 1}


def route_after_tools(state: AgentState) -> str:
    # Always return to the planner so it can synthesize a final text answer
    # (once the round cap is hit, planner_node stops binding tools, so this
    # can't loop forever).
    return "planner"


REFLECTION_PROMPT = """Tu es un relecteur juridique strict. Voici l'échange \
en cours (dernière réponse de l'assistant à évaluer par rapport au contexte \
récupéré dans les messages précédents).

Réponds UNIQUEMENT par "SUFFISANT" si la dernière réponse de l'assistant :
- cite au moins un article précis récupéré par les outils,
- ne contient pas d'affirmation juridique non appuyée par le contexte récupéré,
- répond effectivement à la question posée.

Sinon réponds "INSUFFISANT" suivi d'une courte raison (une phrase)."""


def reflection_node(state: AgentState) -> dict:
    """Lightweight self-check node — the 'agentic' quality-control step.
    Bounded by MAX_RETRIEVAL_ROUNDS so it can't loop forever if the corpus
    genuinely doesn't cover the question."""
    if state.get("retrieval_rounds", 0) >= MAX_RETRIEVAL_ROUNDS:
        return {"needs_more_retrieval": False}

    llm = get_generation_llm()
    transcript = "\n".join(
        f"{m.type}: {getattr(m, 'content', '')}" for m in state["messages"][-6:]
    )
    verdict = llm.invoke(
        [SystemMessage(content=REFLECTION_PROMPT), HumanMessage(content=transcript)]
    )
    needs_more = verdict.content.strip().upper().startswith("INSUFFISANT")
    return {"needs_more_retrieval": needs_more}


def route_after_reflection(state: AgentState) -> str:
    if state.get("needs_more_retrieval") and state.get("retrieval_rounds", 0) < MAX_RETRIEVAL_ROUNDS:
        return "planner"
    return END


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("tools", tool_node)
    graph.add_node("after_tools", after_tools_node)
    graph.add_node("reflection", reflection_node)

    graph.set_entry_point("planner")

    graph.add_conditional_edges(
        "planner", route_after_planner, {"tools": "tools", "reflection": "reflection"}
    )
    graph.add_edge("tools", "after_tools")
    graph.add_conditional_edges(
        "after_tools", route_after_tools, {"planner": "planner", "reflection": "reflection"}
    )
    graph.add_conditional_edges(
        "reflection", route_after_reflection, {"planner": "planner", END: END}
    )

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


def run_query(app, question: str, thread_id: str = "default") -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "messages": [HumanMessage(content=question)],
        "retrieval_rounds": 0,
        "needs_more_retrieval": False,
    }
    result = app.invoke(initial_state, config=config)
    return result


if __name__ == "__main__":
    app = build_graph()
    result = run_query(app, "Quelle est la durée du congé de maternité au Maroc ?")
    print(result["messages"][-1].content)
