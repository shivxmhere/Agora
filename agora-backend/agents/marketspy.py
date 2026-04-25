from typing import Callable
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent

class MarketSpyAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
        
    def run(self, input: str, stream_callback: Callable[[str], None]) -> str:
        prompt = PromptTemplate.from_template(
            "You are a Market Intelligence Expert. I need a competitive analysis and market research summary for: {input}. "
            "Format your output in well-structured markdown with bullet points and sections like: "
            "Overview, Key Competitors, Market Trends, and Opportunities."
        )
        chain = prompt | self.llm
        output = ""
        for chunk in chain.stream({"input": input}):
            content = chunk.content
            output += content
            stream_callback(content)
        return output
