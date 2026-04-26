"""CodeReview Agent — Static analysis engine with multi-pass review.
Unique pipeline: Lint Pass → Security Scan → Complexity Audit → Refactor Suggestions.
Does NOT use web search. Purely LLM-powered code analysis.
"""
import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class CodeReviewAgent(BaseAgent):
    agent_id = "codereview"

    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not self._is_placeholder(groq_key):
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        else:
            self.llm = None

    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        cb = stream_callback or (lambda x: None)

        # ── Pass 1: Lint & Bug Detection ──
        cb("\n🔍 **Pass 1/4 — Lint & Bug Detection...**\n\n")
        lint_prompt = PromptTemplate.from_template(
            "You are a strict linter. Find all bugs, typos, syntax errors, and logic flaws in this code:\n\n{input}\n\n"
            "List each bug with severity (🔴 Critical / 🟡 Warning / 🔵 Info) and line reference."
        )
        lint_report = ""
        for chunk in (lint_prompt | self.llm).stream({"input": input}):
            lint_report += chunk.content

        # ── Pass 2: Security Scan ──
        cb("\n🛡️ **Pass 2/4 — OWASP Security Scan...**\n\n")
        sec_prompt = PromptTemplate.from_template(
            "You are a DAST/SAST security scanner. Check this code for OWASP Top-10 vulnerabilities:\n\n{input}\n\n"
            "Check for: SQL injection, XSS, CSRF, auth bypass, insecure deserialization, broken access control.\n"
            "Output a table: | Vulnerability | Severity | Location | Fix |"
        )
        sec_report = ""
        for chunk in (sec_prompt | self.llm).stream({"input": input}):
            sec_report += chunk.content

        # ── Pass 3: Complexity Audit ──
        cb("\n📐 **Pass 3/4 — Complexity & Performance Audit...**\n\n")
        comp_prompt = PromptTemplate.from_template(
            "Analyze the algorithmic complexity of this code:\n\n{input}\n\n"
            "For each function: provide Big-O time/space, identify hot loops, and suggest optimizations."
        )
        comp_report = ""
        for chunk in (comp_prompt | self.llm).stream({"input": input}):
            comp_report += chunk.content

        # ── Pass 4: Final Verdict — stream to user ──
        cb("\n📋 **Pass 4/4 — Generating Final Verdict...**\n\n")
        final_prompt = PromptTemplate.from_template(
            "Synthesize these 3 audit passes into a single final code review report:\n\n"
            "--- LINT ---\n{lint}\n\n"
            "--- SECURITY ---\n{security}\n\n"
            "--- COMPLEXITY ---\n{complexity}\n\n"
            "Output a clean Markdown report with:\n"
            "## 🔍 Code Review Report\n"
            "### Bugs & Lint Issues\n"
            "### Security Vulnerabilities\n"
            "### Complexity Analysis\n"
            "### Top 3 Refactoring Suggestions (with code examples)\n"
            "### Verdict: Security X/10 | Complexity X/10 | Overall: PASS/NEEDS REVISION/FAIL\n"
        )
        output = ""
        for chunk in (final_prompt | self.llm).stream({"lint": lint_report, "security": sec_report, "complexity": comp_report}):
            content = chunk.content
            output += content
            cb(content)

        return output
