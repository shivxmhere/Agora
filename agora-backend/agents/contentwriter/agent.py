from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class ContentWriterAgent(BaseAgent):
    agent_id = "contentwriter"

    def __init__(self):
        import os
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not self._is_placeholder(groq_key):
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        else:
            self.llm = None

    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        cb = stream_callback or (lambda x: None)

        # Stage 1: Outline
        cb("\n📋 **Stage 1: Creating outline...**\n\n")
        outline_prompt = PromptTemplate.from_template(
            "Create a detailed content outline for: {input}\n"
            "Include: hook, 3-5 main sections, key points per section, CTA."
        )
        outline = ""
        for chunk in (outline_prompt | self.llm).stream({"input": input}):
            outline += chunk.content

        # Stage 2: Draft
        cb("\n✍️ **Stage 2: Drafting content...**\n\n")
        draft_prompt = PromptTemplate.from_template(
            "Using this outline:\n{outline}\n\n"
            "Write the full content for: {input}\n"
            "Make it engaging, specific, and publication-ready."
        )
        draft = ""
        for chunk in (draft_prompt | self.llm).stream({"outline": outline, "input": input}):
            draft += chunk.content

        # Stage 3: Polish — stream this to the user
        cb("\n✨ **Stage 3: Polishing final content...**\n\n")
        polish_prompt = PromptTemplate.from_template(
            "Polish and finalize this content:\n{draft}\n\n"
            "Improve flow, impact, and formatting. Output in clean Markdown."
        )
        output = ""
        for chunk in (polish_prompt | self.llm).stream({"draft": draft}):
            content = chunk.content
            output += content
            cb(content)

        return output
