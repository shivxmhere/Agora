"""DevOps Agent — Infrastructure-as-Code generator.
Unique pipeline: Stack Analysis → Dockerfile Gen → CI/CD Pipeline Gen → Scaling Strategy.
Uses Tavily for latest deployment best practices. Outputs ready-to-copy config files.
"""
import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class DevOpsAgent(BaseAgent):
    agent_id = "devops"

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

        # ── Phase 1: Best Practice Lookup ──
        cb("\n📚 **Phase 1/3 — Fetching latest deployment patterns...**\n\n")
        docs = ""
        if self.tavily_client:
            try:
                res = self.tavily_client.search(f"{input} deployment docker kubernetes best practices 2026", search_depth="basic", max_results=3)
                for r in res.get("results", []):
                    sources.append(r)
                    docs += f"[{r.get('title', '')}]\n{r.get('content', '')[:250]}\n\n"
            except Exception as e:
                cb(f"⚠️ Doc lookup failed: {e}\n")
        if not docs:
            docs = "Standard 12-factor methodology + cloud-native patterns."

        # ── Phase 2: Config Generation ──
        cb("\n🐳 **Phase 2/3 — Generating infrastructure configs...**\n\n")
        config_prompt = PromptTemplate.from_template(
            "For this stack: {input}\nBest practices:\n{docs}\n\n"
            "Generate production-ready configs:\n"
            "1. Multi-stage Dockerfile (with security hardening)\n"
            "2. docker-compose.yml (with health checks)\n"
            "3. GitHub Actions CI/CD pipeline (.github/workflows/deploy.yml)\n"
            "Output each as a fenced code block with the correct language tag."
        )
        configs = ""
        for chunk in (config_prompt | self.llm).stream({"input": input, "docs": docs}):
            configs += chunk.content

        # ── Phase 3: Scaling Strategy — stream to user ──
        cb("\n🚀 **Phase 3/3 — Compiling deployment strategy...**\n\n")
        final_prompt = PromptTemplate.from_template(
            "Compile a complete DevOps deployment guide:\n\n"
            "--- CONFIGS ---\n{configs}\n\n"
            "Stack: {input}\n\n"
            "Output clean Markdown:\n"
            "## ⚙️ DevOps Deployment Guide\n"
            "### 🐳 Dockerfile (Multi-stage, Production-ready)\n"
            "### 📦 Docker Compose\n"
            "### 🔄 CI/CD Pipeline (GitHub Actions)\n"
            "### 📈 Scaling Strategy & Cost Estimates\n"
            "### ⚠️ Common Pitfalls & Contradictions (e.g., performance vs cost tradeoffs)\n"
            "Do NOT add sources — I will append them."
        )
        output = ""
        for chunk in (final_prompt | self.llm).stream({"input": input, "configs": configs}):
            content = chunk.content
            output += content
            cb(content)

        if sources:
            src = "\n\n### 🌐 DevOps References\n"
            for s in sources:
                src += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += src
            cb(src)

        return output
