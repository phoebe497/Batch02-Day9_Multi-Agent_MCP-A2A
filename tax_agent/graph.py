"""Tax Agent LangGraph definition.

Uses create_react_agent with a tax-specialised system prompt.
No tools — it answers purely from LLM knowledge.
"""

from __future__ import annotations

from langgraph.prebuilt import create_react_agent

from common.llm import get_llm

TAX_SYSTEM_PROMPT = """You are a specialist tax attorney and CPA.
IMPORTANT (Exercise 5.3): Keep your response extremely brief, summarizing the tax implications in a maximum of 2 short paragraphs or 100 words.

Areas of expertise:
- Corporate tax law and tax evasion penalties (IRS, FBAR/FATCA)
- Civil vs. criminal penalties and individual executive liability

Always note that your response is for educational purposes."""


def create_graph():
    """Return a compiled LangGraph create_react_agent for tax questions."""
    llm = get_llm()
    graph = create_react_agent(
        model=llm,
        tools=[],
        prompt=TAX_SYSTEM_PROMPT,
    )
    return graph