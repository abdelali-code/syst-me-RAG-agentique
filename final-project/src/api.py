"""
FastAPI layer exposing the Agentic RAG graph over HTTP, for the Flutter client.

Run with:
    uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
"""
import re
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import ToolMessage
from pydantic import BaseModel

from src.graph import build_graph, run_query
from src.tools import list_available_codes
from evaluation.eval_questions import SIMPLE_QUESTIONS, COMPLEX_QUESTIONS

SOURCE_RE = re.compile(r"\[Source:\s*([^\|\]]+?)\s*\|\s*Article\s+([^\|\]]+?)\s*(?:\|[^\]]*)?\]")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.graph = build_graph()
    yield


app = FastAPI(title="Agentic RAG Juridique API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    thread_id: str | None = None


class Source(BaseModel):
    code: str
    article: str


class ChatResponse(BaseModel):
    answer: str
    thread_id: str
    sources: list[Source]


def _extract_sources(messages) -> list[Source]:
    seen: dict[tuple[str, str], Source] = {}
    for message in messages:
        if not isinstance(message, ToolMessage):
            continue
        content = message.content if isinstance(message.content, str) else str(message.content)
        for code, article in SOURCE_RE.findall(content):
            key = (code.strip(), article.strip())
            if key not in seen:
                seen[key] = Source(code=key[0], article=key[1])
    return list(seen.values())


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/codes")
def codes():
    text = list_available_codes.func()
    return {"codes": re.findall(r"^- (.+)$", text, re.MULTILINE)}


@app.get("/eval/questions")
def eval_questions():
    """The 10 simple + 10 complex questions used by evaluation/eval_questions.py,
    reused as-is so the Flutter app's evaluation runner and the CLI eval script
    never drift apart."""
    return {"simple": SIMPLE_QUESTIONS, "complexe": COMPLEX_QUESTIONS}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    thread_id = req.thread_id or str(uuid.uuid4())
    result = run_query(app.state.graph, req.question, thread_id=thread_id)
    answer = result["messages"][-1].content
    return ChatResponse(
        answer=answer,
        thread_id=thread_id,
        sources=_extract_sources(result["messages"]),
    )
