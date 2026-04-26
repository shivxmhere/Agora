import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class CyberSecAgent(BaseAgent):
    agent_id = "cybersec"

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
        
        cb("\n🔐 **Hunting for Vulnerabilities & CVEs...**\n\n")
        sources = []
        context = ""
        if self.tavily_client:
            try:
                res = self.tavily_client.search(f"{input} security vulnerabilities CVE exploits", search_depth="basic", max_results=3)
                for r in res.get("results", []):
                    sources.append(r)
                    context += f"Source: {r.get('url')}\nContent: {r.get('content')}\n\n"
            except Exception as e:
                cb(f"⚠️ Intel gathering failed: {e}\n")
        
        context_block = f"Live Threat Intel:\n{context}" if context else "No live CVEs pulled. Using internal heuristic models."
        
        cb("\n🛡️ **Generating Penetration Test & Security Audit...**\n\n")
        prompt = PromptTemplate.from_template(
            "You are a Senior Penetration Tester and Cyber Security Analyst.\n"
            "Analyze the target architecture, stack, or code: {input}\n\n"
            "Use the following live threat intelligence if relevant:\n{context_block}\n\n"
            "Format:\n"
            "## 🛡️ Security Audit Report\n"
            "### 🛑 Attack Vectors identified\n"
            "### 🐛 CVEs & Known Vulnerabilities (Highlight any contradictions in threat severity)\n"
            "### 🔒 Mitigation Strategies\n"
            "### ⚠️ Overall Risk Score (Out of 10)\n"
        )
        
        output = ""
        for chunk in (prompt | self.llm).stream({"input": input, "context_block": context_block}):
            content = chunk.content
            output += content
            cb(content)
            
        if sources:
            sources_section = "\n\n### 🌐 Threat Intel Sources\n"
            for s in sources:
                sources_section += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += sources_section
            cb(sources_section)
            
        return output
