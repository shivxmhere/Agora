import os
from typing import Callable, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent


class CopywriterAgent(BaseAgent):
    agent_id = "copywriter"

    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not self._is_placeholder(groq_key):
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
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
        
        cb("\n📝 **Fetching SEO Keywords & Marketing Trends...**\n\n")
        sources = []
        context = ""
        if self.tavily_client:
            try:
                # We search for modern examples of whatever the user asked for
                res = self.tavily_client.search(f"{input} SEO marketing copy trends viral hooks", search_depth="basic", max_results=2)
                for r in res.get("results", []):
                    sources.append(r)
                    context += f"Source: {r.get('url')}\nContent: {r.get('content')}\n\n"
            except Exception as e:
                cb(f"⚠️ Search failed: {e}\n")
        
        context_block = f"Live Marketing Trends:\n{context}" if context else "Standard direct-response copywriting principles applied."
        
        cb("\n✍️ **Crafting High-Converting Copy...**\n\n")
        prompt = PromptTemplate.from_template(
            "You are a World-Class Direct Response Copywriter and SEO Specialist.\n"
            "Write high-converting marketing copy for: {input}\n\n"
            "Reference current trends:\n{context_block}\n\n"
            "Format:\n"
            "## ✍️ High-Converting Copy Package\n"
            "### 🪝 A/B Test Hooks (Provide 3 distinct hooks)\n"
            "### 📧 Email Newsletter Draft (Persuasive, PAS framework)\n"
            "### 📱 Social Media Caption (With emojis and hashtags)\n"
            "### 🔍 SEO Keywords & Search Intent (Highlight any SEO strategy contradictions)\n"
            "### 🎯 Call To Action (Strong & Urgent)\n"
        )
        
        output = ""
        for chunk in (prompt | self.llm).stream({"input": input, "context_block": context_block}):
            content = chunk.content
            output += content
            cb(content)
            
        if sources:
            sources_section = "\n\n### 🌐 Marketing References\n"
            for s in sources:
                sources_section += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += sources_section
            cb(sources_section)
            
        return output
