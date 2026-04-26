"""Copywriter Agent — SEO copy engine with A/B testing frameworks.
Unique pipeline: SEO Keyword Research → Hook Generator → Multi-Format Copy → CTA Optimizer.
Uses Tavily for real-time SEO trends. Outputs multiple copy variants.
"""
import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class CopywriterAgent(BaseAgent):
    agent_id = "copywriter"

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

        # ── Phase 1: SEO Keyword Research ──
        cb("\n🔍 **Phase 1/3 — Mining SEO keywords & trending hooks...**\n\n")
        seo_data = ""
        if self.tavily_client:
            try:
                res = self.tavily_client.search(f"{input} SEO keywords marketing copy viral hooks 2026", search_depth="basic", max_results=3)
                for r in res.get("results", []):
                    sources.append(r)
                    seo_data += f"[{r.get('title', '')}]\n{r.get('content', '')[:250]}\n\n"
            except Exception as e:
                cb(f"⚠️ SEO research failed: {e}\n")
        if not seo_data:
            seo_data = "Standard direct-response copywriting principles (PAS, AIDA, 4Ps)."

        # ── Phase 2: Hook + Variant Generation ──
        cb("\n🪝 **Phase 2/3 — Generating A/B hook variants...**\n\n")
        hook_prompt = PromptTemplate.from_template(
            "For this product/service: {input}\nSEO intelligence:\n{seo_data}\n\n"
            "Generate:\n"
            "1. Three A/B test headline hooks (each with different emotional angle)\n"
            "2. Target keyword cluster (5 primary, 10 secondary)\n"
            "3. Search intent mapping (informational/transactional/navigational)"
        )
        hooks = ""
        for chunk in (hook_prompt | self.llm).stream({"input": input, "seo_data": seo_data}):
            hooks += chunk.content

        # ── Phase 3: Full Copy Package — stream to user ──
        cb("\n✍️ **Phase 3/3 — Crafting multi-format copy package...**\n\n")
        final_prompt = PromptTemplate.from_template(
            "Using these A/B hooks and SEO data:\n\n"
            "--- HOOKS ---\n{hooks}\n\n"
            "Product: {input}\n\n"
            "Generate a complete copy package in clean Markdown:\n"
            "## ✍️ Copy Package\n"
            "### 🪝 A/B Test Headlines (3 variants with rationale)\n"
            "### 📧 Email Newsletter (PAS framework: Problem→Agitate→Solve)\n"
            "### 📱 Social Media Captions (Twitter, LinkedIn, Instagram — each unique)\n"
            "### 🔍 SEO Strategy (keywords + search intent + contradictions in SEO advice)\n"
            "### 🎯 CTA Variants (3 urgency levels: soft/medium/hard)\n"
            "Do NOT add sources — I will append them."
        )
        output = ""
        for chunk in (final_prompt | self.llm).stream({"input": input, "hooks": hooks}):
            content = chunk.content
            output += content
            cb(content)

        if sources:
            src = "\n\n### 🌐 Marketing & SEO Sources\n"
            for s in sources:
                src += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += src
            cb(src)

        return output
