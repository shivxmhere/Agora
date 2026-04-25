from agents.base import BaseAgent
from agents.autoresearch.agent import AutoResearchAgent
from agents.codereview.agent import CodeReviewAgent
from agents.contentwriter.agent import ContentWriterAgent
from agents.marketspy import MarketSpyAgent
from agents.dataanalyst import DataAnalystAgent

AGENT_MAP = {
    "autoresearch": AutoResearchAgent,
    "codereview": CodeReviewAgent,
    "contentwriter": ContentWriterAgent,
    "marketspy": MarketSpyAgent,
    "dataanalyst": DataAnalystAgent,
}

class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def get_agent(self, agent_id: str) -> BaseAgent:
        if agent_id not in self.agents:
            if agent_id in AGENT_MAP:
                self.agents[agent_id] = AGENT_MAP[agent_id]()
            else:
                raise ValueError(f"Agent {agent_id} not found in registry.")
        return self.agents[agent_id]

registry = AgentRegistry()
