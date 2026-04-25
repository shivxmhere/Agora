from typing import Callable
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent

class DataAnalystAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        
    def run(self, input: str, stream_callback: Callable[[str], None]) -> str:
        prompt = PromptTemplate.from_template(
            "You are an expert Data Analyst. Analyze this data or description: {input}. "
            "Provide insights, find patterns, and explain key metrics in plain English. "
            "Use markdown formatting with sections like Data Overview, Key Findings, and Actionable Insights."
        )
        chain = prompt | self.llm
        output = ""
        for chunk in chain.stream({"input": input}):
            content = chunk.content
            output += content
            stream_callback(content)
        return output
