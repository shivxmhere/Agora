import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class UXResearcherAgent(BaseAgent):
    agent_id = "uxresearcher"

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
        
        cb("\n👥 **Conducting User Persona & Competitor UX Analysis...**\n\n")
        sources = []
        context = ""
        if self.tavily_client:
            try:
                res = self.tavily_client.search(f"{input} user feedback UX review design patterns", search_depth="basic", max_results=3)
                for r in res.get("results", []):
                    sources.append(r)
                    context += f"Source: {r.get('url')}\nContent: {r.get('content')}\n\n"
            except Exception as e:
                cb(f"⚠️ Intel gathering failed: {e}\n")
        
        context_block = f"Live Market UX Data:\n{context}" if context else "Synthesizing based on standard design heuristics."
        
        cb("\n✨ **Drafting UX Research Report...**\n\n")
        prompt = PromptTemplate.from_template(
            "You are a Senior UX Researcher & Product Designer.\n"
            "Analyze the product idea, user feedback, or feature: {input}\n\n"
            "Use the following live market UX data if relevant:\n{context_block}\n\n"
            "Format:\n"
            "## 🎨 UX Research & Empathy Report\n"
            "### 🙍 User Personas (Generate 2 distinct profiles)\n"
            "### ❤️ Pain Points & Friction (Highlight contradictory user needs if they exist)\n"
            "### 💡 Usability Recommendations & Heuristics\n"
            "### 🚀 Feature Prioritization Matrix\n"
            "### 🏁 Conclusion\n"
        )
        
        output = ""
        for chunk in (prompt | self.llm).stream({"input": input, "context_block": context_block}):
            content = chunk.content
            output += content
            cb(content)
            
        if sources:
            sources_section = "\n\n### 🌐 UX Inspiration & Sources\n"
            for s in sources:
                sources_section += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += sources_section
            cb(sources_section)
            
        return output
