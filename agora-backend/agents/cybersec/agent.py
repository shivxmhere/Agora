"""CyberSec Agent — Threat intelligence + penetration test generator.
Unique pipeline: CVE Recon → Attack Surface Mapping → Exploit Scenario → Hardening Plan.
Uses Tavily for live CVE/vulnerability lookup.
"""
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
        sources = []

        # ── Phase 1: CVE Recon ──
        cb("\n🔐 **Phase 1/3 — Scanning CVE databases & threat feeds...**\n\n")
        threat_intel = ""
        if self.tavily_client:
            try:
                res = self.tavily_client.search(f"{input} CVE vulnerability security advisory 2025 2026", search_depth="basic", max_results=4)
                for r in res.get("results", []):
                    sources.append(r)
                    threat_intel += f"[{r.get('title', '')}]\n{r.get('content', '')[:300]}\n\n"
            except Exception as e:
                cb(f"⚠️ CVE recon failed: {e}\n")
        if not threat_intel:
            threat_intel = "No live CVE data. Running heuristic vulnerability models."

        # ── Phase 2: Attack Surface Mapping ──
        cb("\n🗺️ **Phase 2/3 — Mapping attack surface & exploit paths...**\n\n")
        attack_prompt = PromptTemplate.from_template(
            "Given this target: {input}\nAnd this live threat intelligence:\n{intel}\n\n"
            "Map the attack surface:\n"
            "1. Entry points (APIs, ports, user inputs)\n"
            "2. Privilege escalation paths\n"
            "3. Data exfiltration vectors\n"
            "4. Supply chain risks"
        )
        attack_map = ""
        for chunk in (attack_prompt | self.llm).stream({"input": input, "intel": threat_intel}):
            attack_map += chunk.content

        # ── Phase 3: Final Audit — stream to user ──
        cb("\n🛡️ **Phase 3/3 — Compiling security audit report...**\n\n")
        final_prompt = PromptTemplate.from_template(
            "Compile a professional penetration test report:\n\n"
            "--- THREAT INTEL ---\n{intel}\n\n"
            "--- ATTACK SURFACE ---\n{attack_map}\n\n"
            "Target: {input}\n\n"
            "Output clean Markdown:\n"
            "## 🛡️ Penetration Test & Security Audit\n"
            "### 🛑 Critical Vulnerabilities Found\n"
            "### 🗺️ Attack Surface Map\n"
            "### 🐛 CVEs & Known Exploits (with contradiction notes where severity ratings conflict)\n"
            "### 🔒 Hardening Recommendations (prioritized by impact)\n"
            "### ⚠️ Overall Risk Score: X/10\n"
            "Do NOT add sources — I will append them."
        )
        output = ""
        for chunk in (final_prompt | self.llm).stream({"input": input, "intel": threat_intel, "attack_map": attack_map}):
            content = chunk.content
            output += content
            cb(content)

        if sources:
            src = "\n\n### 🌐 Threat Intelligence Sources\n"
            for s in sources:
                src += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += src
            cb(src)

        return output
