from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class DataAnalystAgent(BaseAgent):
    agent_id = "dataanalyst"

    def __init__(self):
        import os
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not self._is_placeholder(groq_key):
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        else:
            self.llm = None

    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        cb = stream_callback or (lambda x: None)
        prompt = PromptTemplate.from_template(
            "You are an expert Data Analyst. Analyze this data or description: {input}\n\n"
            "Provide a comprehensive analysis in Markdown with these sections:\n"
            "## Data Overview\n"
            "## Key Findings\n"
            "List patterns, trends, anomalies with supporting numbers.\n"
            "## Statistical Insights\n"
            "Correlation analysis, outliers, confidence levels.\n"
            "## Actionable Recommendations\n"
            "3-5 specific, data-driven recommendations.\n"
            "## Next Steps\n"
        )
        output = ""
        for chunk in (prompt | self.llm).stream({"input": input}):
            content = chunk.content
            output += content
            cb(content)
        return output
