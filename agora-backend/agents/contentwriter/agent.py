"""ContentWriter Agent — 3-stage generative pipeline + Tavily trend research.
Unique pipeline: Trend Research → Outline Builder → Draft Writer → Polish & SEO.
Uses web search to find trending hooks BEFORE writing.
"""
import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class ContentWriterAgent(BaseAgent):
    agent_id = "contentwriter"

    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not self._is_placeholder(groq_key):
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        else:
            self.llm = None

        tavily_key = os.getenv("TAVILY_API_KEY", "")
        if not self._is_placeholder(tavily_key):
            try:
                from tavily import TavilyClient
                self.tavily_client = TavilyClient(api_key=tavily_key)
            except Exception:
                self.tavily_client = None
        else:
            self.tavily_client = None

    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        cb = stream_callback or (lambda x: None)
        sources = []

        # ── Stage 1: Trend Research ──
        cb("\n🌐 **Stage 1/4 — Researching trending content hooks...**\n\n")
        trend_context = ""
        if self.tavily_client:
            try:
                res = self.tavily_client.search(f"{input} viral content hooks trending 2026", search_depth="basic", max_results=3)
                for r in res.get("results", []):
                    sources.append(r)
                    trend_context += f"- {r.get('title', '')}: {r.get('content', '')[:200]}\n"
            except Exception as e:
                cb(f"⚠️ Trend research failed: {e}\n")
        if not trend_context:
            trend_context = "No live trends available. Using evergreen content principles."

        # ── Stage 2: Outline ──
        cb("\n📋 **Stage 2/4 — Building content outline...**\n\n")
        outline_prompt = PromptTemplate.from_template(
            "Create a detailed content outline for: {input}\n"
            "Current trending hooks and angles:\n{trends}\n\n"
            "Include: attention-grabbing hook, 3-5 main sections, key stats per section, CTA."
        )
        outline = ""
        for chunk in (outline_prompt | self.llm).stream({"input": input, "trends": trend_context}):
            outline += chunk.content

        # ── Stage 3: Draft ──
        cb("\n✍️ **Stage 3/4 — Drafting full content...**\n\n")
        draft_prompt = PromptTemplate.from_template(
            "Using this outline:\n{outline}\n\n"
            "Write the full content for: {input}\n"
            "Make it engaging, specific, data-backed, and publication-ready."
        )
        draft = ""
        for chunk in (draft_prompt | self.llm).stream({"outline": outline, "input": input}):
            draft += chunk.content

        # ── Stage 4: Polish & stream ──
        cb("\n✨ **Stage 4/4 — Final polish & formatting...**\n\n")
        polish_prompt = PromptTemplate.from_template(
            "Polish and finalize this content:\n{draft}\n\n"
            "Improve flow, impact, and formatting. Output in clean Markdown.\n"
            "Do NOT add a sources section — I will append it."
        )
        output = ""
        for chunk in (polish_prompt | self.llm).stream({"draft": draft}):
            content = chunk.content
            output += content
            cb(content)

        # ── Append sources ──
        if sources:
            sources_section = "\n\n### 🌐 Trend Sources Referenced\n"
            for s in sources:
                sources_section += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += sources_section
            cb(sources_section)

        return output
