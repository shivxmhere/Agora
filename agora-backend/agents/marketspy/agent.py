"""MarketSpy Agent — Competitive intelligence with live web recon.
Unique pipeline: Live Web Recon → SWOT Matrix → Competitor Battlecard → Strategy Brief.
Uses Tavily to pull live competitor data, then multi-pass LLM analysis.
"""
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

        # ── Phase 1: Live Web Recon ──
        cb("\n🕵️ **Phase 1/3 — Deploying market surveillance drones...**\n\n")
        recon = ""
        if self.tavily_client:
            try:
                res = self.tavily_client.search(f"{input} competitors pricing market share 2026", search_depth="basic", max_results=4)
                for r in res.get("results", []):
                    sources.append(r)
                    recon += f"[{r.get('title', '')}] ({r.get('url')})\n{r.get('content', '')[:300]}\n\n"
            except Exception as e:
                cb(f"⚠️ Recon disrupted: {e}\n")
        if not recon:
            recon = "No live recon data. Using baseline competitive models."

        # ── Phase 2: SWOT Analysis ──
        cb("\n📊 **Phase 2/3 — Building SWOT matrix & competitor map...**\n\n")
        swot_prompt = PromptTemplate.from_template(
            "Using this live market intelligence:\n{recon}\n\n"
            "Build a SWOT analysis for: {input}\n"
            "Format as a Markdown table: | Factor | Strengths | Weaknesses | Opportunities | Threats |"
        )
        swot = ""
        for chunk in (swot_prompt | self.llm).stream({"input": input, "recon": recon}):
            swot += chunk.content

        # ── Phase 3: Final Strategy Brief — stream to user ──
        cb("\n🎯 **Phase 3/3 — Generating strategic intelligence brief...**\n\n")
        final_prompt = PromptTemplate.from_template(
            "Compile a final Market Intelligence Report using:\n\n"
            "--- LIVE RECON ---\n{recon}\n\n"
            "--- SWOT ---\n{swot}\n\n"
            "For the target: {input}\n\n"
            "Output clean Markdown:\n"
            "## 🕵️ Market Intelligence Report\n"
            "### 🔎 Market Landscape & Sizing\n"
            "### ⚔️ Competitor Battlecard (table: Competitor | Strength | Gap | Threat Level)\n"
            "### 📊 SWOT Matrix\n"
            "### ⚠️ Contradictions & Conflicting Data (flag where sources disagree)\n"
            "### 💡 Strategic Recommendation\n"
            "Do NOT add sources — I will append them."
        )
        output = ""
        for chunk in (final_prompt | self.llm).stream({"input": input, "recon": recon, "swot": swot}):
            content = chunk.content
            output += content
            cb(content)

        # ── Append Sources ──
        if sources:
            src = "\n\n### 🌐 Intelligence Sources\n"
            for s in sources:
                src += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += src
            cb(src)

        return output
