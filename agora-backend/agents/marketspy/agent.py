import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class MarketSpyAgent(BaseAgent):
    agent_id = "marketspy"

    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not self._is_placeholder(groq_key):
            # Set temperature=0.0 for deterministic results
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        else:
            self.llm = None

    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        cb = stream_callback or (lambda x: None)
        prompt = PromptTemplate.from_template(
            "You are a Competitive Intelligence Agent. Perform a deep market scan for: {input}\n\n"
            "Analyze current competitors, pricing strategies, market sentiment, and upcoming threats.\n\n"
            "Format:\n"
            "## 🕵️ Market Intelligence Report\n"
            "### 🔎 Market Landscape\n"
            "### ⚔️ Competitive Battlecard\n"
            "| Competitor | Strength | Gap |\n"
            "|------------|----------|-----|\n"
            "### 📈 Growth Opportunities\n"
            "### ⚠️ Threat Vectors\n"
            "### 💡 Strategic Recommendation\n"
        )
        output = ""
        for chunk in (prompt | self.llm).stream({"input": input}):
            content = chunk.content
            output += content
            cb(content)
        return output
