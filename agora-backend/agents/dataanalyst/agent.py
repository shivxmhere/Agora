"""DataAnalyst Agent — Structured data processing engine.
Unique pipeline: Data Parsing → Statistical Modeling → Anomaly Detection → Recommendations.
Accepts raw CSV/JSON/text data pasted directly. No web search — pure analytical engine.
"""
import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class DataAnalystAgent(BaseAgent):
    agent_id = "dataanalyst"

    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not self._is_placeholder(groq_key):
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        else:
            self.llm = None

    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        cb = stream_callback or (lambda x: None)

        # ── Pass 1: Data Parsing & Schema Detection ──
        cb("\n📁 **Pass 1/3 — Parsing uploaded data & detecting schema...**\n\n")
        parse_prompt = PromptTemplate.from_template(
            "You are a data engineer. Parse and understand this raw data (could be CSV, JSON, table, or text):\n\n"
            "{input}\n\n"
            "Output:\n"
            "1. Detected format (CSV / JSON / freeform)\n"
            "2. Number of records/rows\n"
            "3. Column names and data types\n"
            "4. Summary statistics (mean, median, min, max for numeric columns)\n"
            "5. Any data quality issues (nulls, duplicates, type mismatches)"
        )
        schema = ""
        for chunk in (parse_prompt | self.llm).stream({"input": input}):
            schema += chunk.content

        # ── Pass 2: Pattern & Anomaly Detection ──
        cb("\n📈 **Pass 2/3 — Running pattern recognition & anomaly detection...**\n\n")
        analysis_prompt = PromptTemplate.from_template(
            "Given this data schema:\n{schema}\n\nAnd raw data:\n{input}\n\n"
            "Perform deep analysis:\n"
            "1. Trend analysis (growth/decline patterns)\n"
            "2. Correlation detection between variables\n"
            "3. Anomaly/outlier identification with explanation\n"
            "4. Contradictions in the data (conflicting trends, inconsistent values)\n"
            "5. Seasonal patterns if time-series data"
        )
        analysis = ""
        for chunk in (analysis_prompt | self.llm).stream({"schema": schema, "input": input}):
            analysis += chunk.content

        # ── Pass 3: Final Report — stream to user ──
        cb("\n📊 **Pass 3/3 — Generating insights report...**\n\n")
        report_prompt = PromptTemplate.from_template(
            "Synthesize these analysis passes into a professional data report:\n\n"
            "--- SCHEMA ---\n{schema}\n\n"
            "--- ANALYSIS ---\n{analysis}\n\n"
            "Output clean Markdown:\n"
            "## 📊 Data Analysis Report\n"
            "### 📁 Data Summary\n"
            "### 📈 Key Trends & Metrics\n"
            "### ⚠️ Anomalies & Contradictions\n"
            "### 🎯 Actionable Recommendations (3-5 specific actions)\n"
            "### 💡 Conclusion\n"
        )
        output = ""
        for chunk in (report_prompt | self.llm).stream({"schema": schema, "analysis": analysis}):
            content = chunk.content
            output += content
            cb(content)

        return output
