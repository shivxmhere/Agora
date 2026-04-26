"""UXResearcher Agent — User empathy engine.
Unique pipeline: Competitor UX Scan → Persona Builder → Heuristic Evaluation → Feature Prioritization.
Uses Tavily for competitor UX pattern research.
"""
import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class UXResearcherAgent(BaseAgent):
    agent_id = "uxresearcher"

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

        # ── Phase 1: Competitor UX Scan ──
        cb("\n👀 **Phase 1/3 — Scanning competitor UX patterns...**\n\n")
        ux_intel = ""
        if self.tavily_client:
            try:
                res = self.tavily_client.search(f"{input} UX design user experience review feedback", search_depth="basic", max_results=3)
                for r in res.get("results", []):
                    sources.append(r)
                    ux_intel += f"[{r.get('title', '')}]\n{r.get('content', '')[:250]}\n\n"
            except Exception as e:
                cb(f"⚠️ UX scan disrupted: {e}\n")
        if not ux_intel:
            ux_intel = "No live UX data. Using Nielsen Norman Group heuristics as baseline."

        # ── Phase 2: Persona + Pain Points ──
        cb("\n🙍 **Phase 2/3 — Building user personas & pain point map...**\n\n")
        persona_prompt = PromptTemplate.from_template(
            "For this product/feature: {input}\n\nUX intelligence:\n{intel}\n\n"
            "Generate 2 detailed user personas with:\n"
            "- Name, age, occupation, tech proficiency\n"
            "- Goals & motivations\n"
            "- Frustrations & pain points\n"
            "- A day-in-the-life scenario\n\n"
            "Then list the top 5 friction points these users would face, noting any contradictions "
            "where Persona A's need conflicts with Persona B's need."
        )
        personas = ""
        for chunk in (persona_prompt | self.llm).stream({"input": input, "intel": ux_intel}):
            personas += chunk.content

        # ── Phase 3: Final Report — stream to user ──
        cb("\n🎨 **Phase 3/3 — Generating UX research report...**\n\n")
        final_prompt = PromptTemplate.from_template(
            "Compile a professional UX research deliverable:\n\n"
            "--- UX INTELLIGENCE ---\n{intel}\n\n"
            "--- PERSONAS ---\n{personas}\n\n"
            "Product: {input}\n\n"
            "Output clean Markdown:\n"
            "## 🎨 UX Research Report\n"
            "### 🙍 User Personas\n"
            "### ❤️ Pain Points & Friction Map\n"
            "### ⚠️ Contradictory User Needs (where personas conflict)\n"
            "### 💡 Usability Recommendations (Nielsen's 10 heuristics)\n"
            "### 🚀 Feature Prioritization Matrix (Must/Should/Could/Won't)\n"
            "Do NOT add sources — I will append them."
        )
        output = ""
        for chunk in (final_prompt | self.llm).stream({"input": input, "intel": ux_intel, "personas": personas}):
            content = chunk.content
            output += content
            cb(content)

        if sources:
            src = "\n\n### 🌐 UX Research Sources\n"
            for s in sources:
                src += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += src
            cb(src)

        return output
