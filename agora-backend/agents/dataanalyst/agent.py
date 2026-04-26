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
            # Set temperature=0.0 for deterministic battle mode results
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        else:
            self.llm = None

    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        cb = stream_callback or (lambda x: None)
        
        # Check if the user is asking to upload an attachment but didn't provide text
        if "upload" in input.lower() and "file" in input.lower() and len(input) < 100:
            msg = "⚠️ **No Data Detected:** It looks like you want to upload a file. The UI currently requires passing data as text. Please open your CSV, JSON, or text file, copy the contents, and paste them directly into this input box. I will process them instantly!"
            cb(msg)
            return msg

        cb("\n📊 **Crunching Data Uploads...**\n\n")

        prompt = PromptTemplate.from_template(
            "You are a Senior Data Scientist. Analyze the following user request and any embedded dataset (CSV, JSON, or text): {input}\n\n"
            "Constraints:\n"
            "1. Output clean, professional Markdown.\n"
            "2. Be mathematically precise.\n"
            "3. Note any contradictions or anomalies found in the dataset.\n"
            "4. If real numbers aren't provided but standard metrics are, perform high-fidelity statistical modeling based on market standards.\n\n"
            "Structure:\n"
            "## 📊 Data Insights Report\n"
            "### 📁 Uploaded Data Summary\n"
            "### 📈 Growth Metrics & Trend Analysis\n"
            "### ⚠️ Anomaly Detection & Contradictions (Highlight data irregularities)\n"
            "### 🎯 Predictive Recommendations\n"
            "### 💡 Conclusion\n"
        )
        output = ""
        for chunk in (prompt | self.llm).stream({"input": input}):
            content = chunk.content
            output += content
            cb(content)
        return output
