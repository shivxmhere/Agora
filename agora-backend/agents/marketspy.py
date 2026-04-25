from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class MarketSpyAgent(BaseAgent):
    agent_id = "marketspy"

    def __init__(self):
        import os
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not self._is_placeholder(groq_key):
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
        else:
            self.llm = None

    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        cb = stream_callback or (lambda x: None)
        prompt = PromptTemplate.from_template(
            "You are a Market Intelligence Expert. Provide a comprehensive competitive analysis for: {input}\n\n"
            "Format in Markdown with these sections:\n"
            "## Company/Market Overview\n"
            "## Market Size & Growth\n"
            "## Key Competitors\n"
            "Competitor comparison table: Name | Strength | Weakness | Market Share\n"
            "## SWOT Analysis\n"
            "## Strategic Opportunities\n"
            "## Conclusion\n"
        )
        output = ""
        for chunk in (prompt | self.llm).stream({"input": input}):
            content = chunk.content
            output += content
            cb(content)
        return output
