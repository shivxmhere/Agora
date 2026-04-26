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
        
        cb("\n⚖️ **Reviewing Precedents & Legal Frameworks...**\n\n")
        sources = []
        context = ""
        if self.tavily_client:
            try:
                # We search for modern examples of whatever the user asked for
                res = self.tavily_client.search(f"{input} legal compliance terms privacy standard template 2026", search_depth="basic", max_results=2)
                for r in res.get("results", []):
                    sources.append(r)
                    context += f"Source: {r.get('url')}\nContent: {r.get('content')}\n\n"
            except Exception as e:
                cb(f"⚠️ Search failed: {e}\n")
        
        context_block = f"Live Precedent Data:\n{context}" if context else "Standard boilerplate templates applied."
        
        cb("\n📜 **Drafting Legal Analysis & Boilerplate...**\n\n")
        prompt = PromptTemplate.from_template(
            "You are an AI Legal Tech Assistant. IMPORTANT: You are NOT a lawyer. All outputs must contain strict disclaimers.\n"
            "Draft boilerplate or analyze the following standard agreement / request: {input}\n\n"
            "Reference modern compliance (GDPR, CCPA) using:\n{context_block}\n\n"
            "Format:\n"
            "## 📜 Legal Draft & Analysis Report\n"
            "**⚠️ STRICT DISCLAIMER: This is AI-generated draft text, NOT legal advice. Consult a qualified attorney before use.**\n\n"
            "### 📝 Requested Draft / Boilerplate Clause\n"
            "### ⚖️ Compliance Checklist (GDPR/CCPA/etc.)\n"
            "### ❌ Potential Liabilities & Contradictions (Highlight legal ambiguities)\n"
            "### ✔️ Standard Next Steps\n"
        )
        
        output = ""
        for chunk in (prompt | self.llm).stream({"input": input, "context_block": context_block}):
            content = chunk.content
            output += content
            cb(content)
            
        if sources:
            sources_section = "\n\n### 🌐 Legal Templates Referenced\n"
            for s in sources:
                sources_section += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += sources_section
            cb(sources_section)
            
        return output
