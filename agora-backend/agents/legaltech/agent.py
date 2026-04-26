"""LegalTech Agent — Compliance & contract drafting engine.
Unique pipeline: Precedent Search → Clause Generator → Compliance Check → Risk Assessment.
Uses Tavily for live legal precedent lookup. Includes mandatory AI disclaimers.
"""
import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class LegalTechAgent(BaseAgent):
    agent_id = "legaltech"

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

        # ── Phase 1: Precedent Lookup ──
        cb("\n⚖️ **Phase 1/3 — Searching legal precedents & frameworks...**\n\n")
        precedents = ""
        if self.tavily_client:
            try:
                res = self.tavily_client.search(f"{input} legal template compliance contract standard clause", search_depth="basic", max_results=3)
                for r in res.get("results", []):
                    sources.append(r)
                    precedents += f"[{r.get('title', '')}]\n{r.get('content', '')[:250]}\n\n"
            except Exception as e:
                cb(f"⚠️ Precedent search failed: {e}\n")
        if not precedents:
            precedents = "Standard contract law principles (common law + GDPR/CCPA baseline)."

        # ── Phase 2: Draft Generation ──
        cb("\n📝 **Phase 2/3 — Drafting legal clauses...**\n\n")
        draft_prompt = PromptTemplate.from_template(
            "For this request: {input}\nPrecedents:\n{precedents}\n\n"
            "Draft the requested legal document/clause.\n"
            "Include standard protective language and define all key terms."
        )
        draft = ""
        for chunk in (draft_prompt | self.llm).stream({"input": input, "precedents": precedents}):
            draft += chunk.content

        # ── Phase 3: Compliance & Risk — stream to user ──
        cb("\n🔍 **Phase 3/3 — Running compliance audit...**\n\n")
        final_prompt = PromptTemplate.from_template(
            "Compile a full legal analysis report:\n\n"
            "--- DRAFT ---\n{draft}\n\n"
            "Request: {input}\n\n"
            "Output clean Markdown:\n"
            "## 📜 Legal Analysis & Draft Report\n\n"
            "**⚠️ DISCLAIMER: This is AI-generated text for reference only. It is NOT legal advice. "
            "Consult a qualified attorney before using any clause in production.**\n\n"
            "### 📝 Generated Draft / Boilerplate\n"
            "### ⚖️ Compliance Checklist (GDPR / CCPA / SOC2)\n"
            "### ❌ Risk Assessment & Contradictions (flag ambiguous clauses)\n"
            "### ✔️ Recommended Next Steps\n"
            "Do NOT add sources — I will append them."
        )
        output = ""
        for chunk in (final_prompt | self.llm).stream({"input": input, "draft": draft}):
            content = chunk.content
            output += content
            cb(content)

        if sources:
            src = "\n\n### 🌐 Legal Precedent Sources\n"
            for s in sources:
                src += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += src
            cb(src)

        return output
