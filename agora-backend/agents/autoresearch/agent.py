import os
import concurrent.futures
from typing import Callable, TypedDict, List, Dict, Any, Optional
from bs4 import BeautifulSoup
import requests
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings
from agents.base import BaseAgent


class ResearchState(TypedDict):
    query: str
    sources: List[Dict[str, str]]
    content: List[Dict[str, str]]
    analysis: str
    report: str
    stream_callback: Any


class AutoResearchAgent(BaseAgent):
    agent_id = "autoresearch"

    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not self._is_placeholder(groq_key):
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        else:
            self.llm = None

        self.embeddings = FakeEmbeddings(size=1536)
        tavily_key = os.getenv("TAVILY_API_KEY", "")
        
        if not self._is_placeholder(tavily_key):
            try:
                from tavily import TavilyClient
                self.tavily_client = TavilyClient(api_key=tavily_key)
            except Exception:
                self.tavily_client = None
        else:
            self.tavily_client = None

        if self.llm:
            self.graph = self._build_graph()
        else:
            self.graph = None

    def _build_graph(self):
        workflow = StateGraph(ResearchState)
        workflow.add_node("search", self.search_node)
        workflow.add_node("reader", self.reader_node)
        workflow.add_node("analyst", self.analyst_node)
        workflow.add_node("fact_checker", self.fact_checker_node)
        workflow.add_node("reporter", self.reporter_node)
        workflow.set_entry_point("search")
        workflow.add_edge("search", "reader")
        workflow.add_edge("reader", "analyst")
        workflow.add_edge("analyst", "fact_checker")
        workflow.add_edge("fact_checker", "reporter")
        workflow.add_edge("reporter", END)
        return workflow.compile()

    def search_node(self, state: ResearchState) -> Dict:
        state["stream_callback"]("\n🔍 **Searching the web...**\n")
        if not self.tavily_client:
            state["stream_callback"]("⚠️ [Search skipped: No valid Tavily API key found]\n")
            return {"sources": []}
            
        try:
            response = self.tavily_client.search(
                state["query"], search_depth="advanced", max_results=5
            )
            sources = [
                {"url": r["url"], "title": r.get("title", "")}
                for r in response.get("results", [])
            ]
        except Exception as e:
            sources = []
            state["stream_callback"](f"⚠️ [Search warning: {e}]\n")
        return {"sources": sources}

    def _scrape_url(self, url):
        try:
            res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            text = " ".join(p.get_text() for p in soup.find_all("p"))
            return {"url": url, "text": text[:3000]}
        except Exception:
            return {"url": url, "text": ""}

    def reader_node(self, state: ResearchState) -> Dict:
        state["stream_callback"]("\n📖 **Reading sources...**\n")
        urls = [s["url"] for s in state["sources"]]
        content = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            for res in ex.map(self._scrape_url, urls):
                if res["text"]:
                    content.append(res)
        return {"content": content}

    def analyst_node(self, state: ResearchState) -> Dict:
        state["stream_callback"]("\n🧠 **Analyzing content...**\n")
        texts = [doc["text"] for doc in state["content"]]
        if texts:
            vs = FAISS.from_texts(texts, self.embeddings)
            docs = vs.similarity_search(state["query"], k=3)
            context = "\n".join(d.page_content for d in docs)
        else:
            context = "No content available — using LLM knowledge."
        prompt = PromptTemplate.from_template(
            "Analyze this content regarding '{query}':\n{context}\n"
            "Find patterns and identify knowledge gaps."
        )
        analysis = ""
        for chunk in (prompt | self.llm).stream({"query": state["query"], "context": context}):
            analysis += chunk.content
        return {"analysis": analysis}

    def fact_checker_node(self, state: ResearchState) -> Dict:
        state["stream_callback"]("\n✅ **Fact-checking claims...**\n")
        prompt = PromptTemplate.from_template(
            "Based on the following analysis, extract 5 key claims and provide "
            "confidence scores (1-100%).\nAnalysis:\n{analysis}"
        )
        claims = ""
        for chunk in (prompt | self.llm).stream({"analysis": state["analysis"]}):
            claims += chunk.content
        return {"analysis": claims}

    def reporter_node(self, state: ResearchState) -> Dict:
        state["stream_callback"]("\n📄 **Generating final report...**\n\n")
        sources_text = "\n".join(s.get("url", "") for s in state["sources"])
        prompt = PromptTemplate.from_template(
            "Write a final markdown report for the query: '{query}'.\n"
            "Include headers: ## Summary, ## Key Findings, ## Sources\n"
            "Verified data:\n{analysis}\nSources:\n{sources}"
        )
        report = ""
        for chunk in (prompt | self.llm).stream(
            {"query": state["query"], "analysis": state["analysis"], "sources": sources_text}
        ):
            content = chunk.content
            report += content
            state["stream_callback"](content)
        return {"report": report}

    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        cb = stream_callback or (lambda x: None)
        state = {
            "query": input,
            "sources": [],
            "content": [],
            "analysis": "",
            "report": "",
            "stream_callback": cb,
        }
        result = self.graph.invoke(state)
        return result["report"]
