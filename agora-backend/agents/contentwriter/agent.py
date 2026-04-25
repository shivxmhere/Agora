from typing import Callable, TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from agents.base import BaseAgent

class ContentState(TypedDict):
    topic: str
    format: str
    outline: str
    draft: str
    final_content: str
    stream_callback: Any  # Callable[[str], None]

class ContentWriterAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ContentState)
        
        workflow.add_node("outline", self.outline_node)
        workflow.add_node("draft", self.draft_node)
        workflow.add_node("polish", self.polish_node)
        
        workflow.set_entry_point("outline")
        workflow.add_edge("outline", "draft")
        workflow.add_edge("draft", "polish")
        workflow.add_edge("polish", END)
        
        return workflow.compile()

    def outline_node(self, state: ContentState) -> Dict:
        state["stream_callback"]("\\n*Creating outline...*\\n\\n")
        prompt = PromptTemplate.from_template("Create an outline for a {format} about: {topic}")
        chain = prompt | self.llm
        outline = ""
        for chunk in chain.stream({"format": state.get("format", "blog"), "topic": state["topic"]}):
            content = chunk.content
            outline += content
            state["stream_callback"](content)
        return {"outline": outline}

    def draft_node(self, state: ContentState) -> Dict:
        state["stream_callback"]("\\n\\n*Writing draft...*\\n\\n")
        prompt = PromptTemplate.from_template("Write a {format} using this outline:\\n{outline}")
        chain = prompt | self.llm
        draft = ""
        for chunk in chain.stream({"format": state.get("format", "blog"), "outline": state["outline"]}):
            content = chunk.content
            draft += content
            state["stream_callback"](content)
        return {"draft": draft}

    def polish_node(self, state: ContentState) -> Dict:
        state["stream_callback"]("\\n\\n*Polishing content...*\\n\\n")
        prompt = PromptTemplate.from_template("Polish this draft, making it engaging and adding good hooks. Here is the draft:\\n{draft}")
        chain = prompt | self.llm
        final_content = ""
        for chunk in chain.stream({"draft": state["draft"]}):
            content = chunk.content
            final_content += content
            state["stream_callback"](content)
        return {"final_content": final_content}

    def run(self, input: str, stream_callback: Callable[[str], None]) -> str:
        # We could parse "format" and "topic" if it's passed as JSON, but let's assume input is topic
        # and default format is blog post for simplicity.
        
        import json
        format_type = "blog"
        topic = input
        try:
            parsed = json.loads(input)
            if "topic" in parsed:
                topic = parsed["topic"]
            if "format" in parsed:
                format_type = parsed["format"]
        except:
            pass

        state = {
            "topic": topic,
            "format": format_type,
            "outline": "",
            "draft": "",
            "final_content": "",
            "stream_callback": stream_callback
        }
        
        result = self.graph.invoke(state)
        # We don't need to return the whole raw log, let's just return what was streamed in the process realistically,
        # but the abstract says return final string so we'll just return the final content.
        return f"# Outline\\n{result['outline']}\\n# Draft\\n{result['draft']}\\n# Final Content\\n{result['final_content']}"
