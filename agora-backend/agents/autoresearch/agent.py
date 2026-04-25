import os
import concurrent.futures
from typing import Callable, TypedDict, List, Dict, Any
from bs4 import BeautifulSoup
import requests
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings # using fake for speed/simplicity since no text embedding model was specified or required in env
from agents.base import BaseAgent
from tavily import TavilyClient

class ResearchState(TypedDict):
    query: str
    sources: List[Dict[str, str]]
    content: List[Dict[str, str]]
    analysis: str
    report: str
    stream_callback: Any

class AutoResearchAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        # Using a dummy embedding for FAISS to make it work without extra API keys and keep it fast
        self.embeddings = FakeEmbeddings(size=1536)
        
        tavily_api_key = os.getenv("TAVILY_API_KEY", "dummy")
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        
        self.graph = self._build_graph()

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
        state["stream_callback"]("\n[Searching web...]\n")
        query = state["query"]
        try:
            # Tavily search
            response = self.tavily_client.search(query, search_depth="advanced", max_results=5)
            sources = [{"url": res["url"], "title": res.get("title", "")} for res in response.get("results", [])]
        except Exception as e:
            sources = []
            state["stream_callback"](f"[Tavily search failed: {str(e)}]\n")
            
        return {"sources": sources}

    def _scrape_url(self, url):
        try:
            res = requests.get(url, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            text = ' '.join(p.get_text() for p in soup.find_all('p'))
            return {"url": url, "text": text[:3000]} # Limit length
        except:
            return {"url": url, "text": ""}

    def reader_node(self, state: ResearchState) -> Dict:
        state["stream_callback"]("\n[Reading sources...]\n")
        sources = state["sources"]
        content = []
        
        urls = [s["url"] for s in sources]
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self._scrape_url, urls))
            
        for res in results:
            if res["text"]:
                content.append(res)
                
        return {"content": content}

    def analyst_node(self, state: ResearchState) -> Dict:
        state["stream_callback"]("\n[Analyzing content...]\n")
        texts = [doc["text"] for doc in state["content"]]
        
        if texts:
            # Simple FAISS usage for hackathon
            vectorstore = FAISS.from_texts(texts, self.embeddings)
            docs = vectorstore.similarity_search(state["query"], k=3)
            context = "\n".join([d.page_content for d in docs])
        else:
            context = "No content available."

        prompt = PromptTemplate.from_template("Analyze this content regarding '{query}':\n{context}\nFind patterns and identify knowledge gaps.")
        chain = prompt | self.llm
        analysis = ""
        for chunk in chain.stream({"query": state["query"], "context": context}):
            analysis += chunk.content
            
        state["stream_callback"]("[Done analyzing]\n")
        return {"analysis": analysis}

    def fact_checker_node(self, state: ResearchState) -> Dict:
        state["stream_callback"]("\n[Fact-checking claims...]\n")
        prompt = PromptTemplate.from_template("Based on the following analysis, extract 5 key claims and provide confidence scores (1-100%). Analysis:\n{analysis}")
        chain = prompt | self.llm
        claims = ""
        for chunk in chain.stream({"analysis": state["analysis"]}):
            claims += chunk.content
            
        return {"analysis": claims} # pass the claims forward

    def reporter_node(self, state: ResearchState) -> Dict:
        state["stream_callback"]("\n[Generating final report...]\n\n")
        prompt = PromptTemplate.from_template(
            "Write a final markdown report for the query: '{query}'.\n"
            "Include these exact headers:\n"
            "## Summary\n"
            "## Key Findings\n"
            "## Sources\n\n"
            "Use this verified data:\n{analysis}\n"
            "Sources list:\n{sources}"
        )
        sources_text = "\n".join([s.get("url", "") for s in state["sources"]])
        chain = prompt | self.llm
        report = ""
        for chunk in chain.stream({"query": state["query"], "analysis": state["analysis"], "sources": sources_text}):
            content = chunk.content
            report += content
            state["stream_callback"](content)
            
        return {"report": report}

    def run(self, input: str, stream_callback: Callable[[str], None]) -> str:
        state = {
            "query": input,
            "sources": [],
            "content": [],
            "analysis": "",
            "report": "",
            "stream_callback": stream_callback
        }
        result = self.graph.invoke(state)
        return result["report"]
