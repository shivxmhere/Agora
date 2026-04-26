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
        
        cb("\n⚙️ **Scanning Architecture Best Practices...**\n\n")
        sources = []
        context = ""
        if self.tavily_client:
            try:
                # We search for modern examples of whatever the user asked for
                res = self.tavily_client.search(f"{input} best practices architecture kubernetes docker Github actions", search_depth="basic", max_results=2)
                for r in res.get("results", []):
                    sources.append(r)
                    context += f"Source: {r.get('url')}\nContent: {r.get('content')}\n\n"
            except Exception as e:
                cb(f"⚠️ Search failed: {e}\n")
        
        context_block = f"Live Docs:\n{context}" if context else "Standard architecture patterns applied."
        
        cb("\n🛠️ **Generating Infrastructure Blueprints...**\n\n")
        prompt = PromptTemplate.from_template(
            "You are a Principal DevOps & Cloud Infrastructure Engineer.\n"
            "Build infrastructure configs and CI/CD pipelines for: {input}\n\n"
            "Reference modern practices:\n{context_block}\n\n"
            "Format:\n"
            "## ⚙️ DevOps & Cloud Architecture Plan\n"
            "### 🏗️ Architecture Overview\n"
            "### 🐳 Docker/Containerization Strategy (Provide sample Dockerfile)\n"
            "### 🚀 CI/CD Pipeline (Provide sample GitHub Actions YAML)\n"
            "### 🌩️ Deployment / Kubernetes Manifests (Show snippets)\n"
            "### ⚠️ Scalability & Cost Warnings (Highlight contradicting scaling theories if applicable)\n"
        )
        
        output = ""
        for chunk in (prompt | self.llm).stream({"input": input, "context_block": context_block}):
            content = chunk.content
            output += content
            cb(content)
            
        if sources:
            sources_section = "\n\n### 🌐 Architecture References\n"
            for s in sources:
                sources_section += f"- [{s.get('title', 'Link')}]({s.get('url')})\n"
            output += sources_section
            cb(sources_section)
            
        return output
