from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class CodeReviewAgent(BaseAgent):
    agent_id = "codereview"

    def __init__(self):
        import os
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not self._is_placeholder(groq_key):
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        else:
            self.llm = None

    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        prompt = PromptTemplate.from_template(
            "You are a senior software engineer performing a code review.\n"
            "Analyze this code thoroughly:\n\n{input}\n\n"
            "Provide a detailed review in Markdown with these sections:\n"
            "## Issues Found\n"
            "List each issue with severity (🔴 Critical / 🟡 Warning / 🔵 Info), "
            "line reference if applicable, and explanation.\n"
            "## Security Analysis\n"
            "OWASP top 10 check, input validation, injection risks.\n"
            "## Complexity Analysis\n"
            "Big-O analysis, refactoring opportunities.\n"
            "## Improvement Suggestions\n"
            "Concrete code examples for top 3 improvements.\n"
            "## Verdict\n"
            "Security Score: X/10 | Complexity Score: X/10 | Overall: PASS/NEEDS REVISION/FAIL\n"
        )
        output = ""
        cb = stream_callback or (lambda x: None)
        for chunk in (prompt | self.llm).stream({"input": input}):
            content = chunk.content
            output += content
            cb(content)
        return output
