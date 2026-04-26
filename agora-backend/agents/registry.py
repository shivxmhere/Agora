from agents.base import BaseAgent
from agents.autoresearch.agent import AutoResearchAgent
from agents.codereview.agent import CodeReviewAgent
from agents.contentwriter.agent import ContentWriterAgent
from agents.marketspy.agent import MarketSpyAgent
from agents.dataanalyst.agent import DataAnalystAgent

AGENT_MAP = {
    "autoresearch": AutoResearchAgent,
    "codereview": CodeReviewAgent,
    "contentwriter": ContentWriterAgent,
    "marketspy": MarketSpyAgent,
    "dataanalyst": DataAnalystAgent,
}

class AgentRegistry:
    def __init__(self):
        self._agents = {}

    def get_agent(self, agent_id: str) -> BaseAgent:
        if agent_id not in self._agents:
            if agent_id not in AGENT_MAP:
                raise ValueError(f"Agent '{agent_id}' not found in registry.")
            self._agents[agent_id] = AGENT_MAP[agent_id]()
        return self._agents[agent_id]

registry = AgentRegistry()

# Convenience function used by runner
def get_agent(agent_id: str) -> BaseAgent:
    return registry.get_agent(agent_id)
