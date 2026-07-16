"""
LLM wrapper for xAI's Grok models.

xAI exposes an OpenAI-compatible /v1/chat/completions endpoint, so we reuse
langchain-openai's ChatOpenAI client and simply point it at api.x.ai. This
also gives us native LangChain tool-calling support for the LangGraph agent.

Docs: https://docs.x.ai/docs/api-reference
"""
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY")
XAI_BASE_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
XAI_MODEL = os.getenv("XAI_MODEL", "grok-4-fast")


def get_llm(temperature: float = 0.1, model: str | None = None) -> ChatOpenAI:
    """Return a LangChain-compatible chat model backed by Grok.

    temperature=0.1 by default: legal Q&A should be precise/deterministic,
    not creative.
    """
    if not XAI_API_KEY:
        raise RuntimeError(
            "XAI_API_KEY is not set. Copy .env.example to .env and add your "
            "xAI API key (https://console.x.ai)."
        )
    return ChatOpenAI(
        model=model or XAI_MODEL,
        api_key=XAI_API_KEY,
        base_url=XAI_BASE_URL,
        temperature=temperature,
    )


def get_planner_llm() -> ChatOpenAI:
    """Slightly higher temperature for the planning/reasoning node,
    where a bit more flexibility in decomposing the question helps."""
    return get_llm(temperature=0.3)


def get_generation_llm() -> ChatOpenAI:
    """Low temperature for the final answer generation, to stay grounded
    in retrieved legal text and avoid hallucinated articles."""
    return get_llm(temperature=0.0)
