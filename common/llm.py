"""Shared LLM factory for all agents.

Uses Groq API, so the model and API key can be selected via environment variables.
"""

import os

from langchain_openai import ChatOpenAI


def get_llm() -> ChatOpenAI:
    """Return a ChatOpenAI client pointed at Groq."""
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        openai_api_key=os.getenv("MISTRAL_API_KEY"),
        openai_api_base="https://api.mistral.ai/v1",
        temperature=0.3,
     )