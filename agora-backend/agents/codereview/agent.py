from typing import Callable
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent
import os

class CodeReviewAgent(BaseAgent):
    def __init__(self):
        # We assume the API key is configured or in env
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        
    def run(self, input: str, stream_callback: Callable[[str], None]) -> str:
        prompt = PromptTemplate.from_template(
            "You are an expert Code Reviewer. Analyze the following code snippet. "
            "Format your output exactly with these markdown headers:\n"
            "## Issues Found\n"
            "## Security\n"
            "## Improvements\n"
            "## Verdict\n\n"
            "Code snippet:\n{code}"
        )
        
        chain = prompt | self.llm
        
        output = ""
        for chunk in chain.stream({"code": input}):
            content = chunk.content
            output += content
            stream_callback(content)
            
        return output
