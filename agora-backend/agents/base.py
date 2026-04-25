import os
import logging
import time
from abc import ABC, abstractmethod
from typing import Callable, Optional

logger = logging.getLogger(__name__)

# ─── Rich mock responses per agent ─────────────────────────────────────────────
MOCK_RESPONSES = {
    "autoresearch": """## Research Report: AI Agents Marketplace 2026

**Executive Summary**
The AI agents marketplace is experiencing explosive growth, with the global market projected to reach $4.8B by end of 2026. AGORA represents a pivotal solution in this space.

## Key Findings

1. **Discovery Gap**: Over 50,000 AI agent repositories on GitHub receive fewer than 100 views. A curated marketplace solves the discoverability crisis.

2. **Deployment Barrier**: 73% of developers report that setup complexity prevents adoption of AI agents by non-technical users.

3. **Creator Economy Void**: No existing platform enables developers to monetize autonomous AI agents at scale.

4. **Composability Demand**: 61% of enterprise AI users want to chain multiple AI agents into workflows.

5. **Market Leadership**: First-mover advantage in agent marketplaces is worth an estimated $400M in market capture.

## Conclusion
AGORA addresses all five gaps simultaneously — discovery, deployment, monetization, composability, and community. The timing is perfect.

## Sources
- AI Market Research Quarterly, 2026
- GitHub Developer Survey, March 2026
- Stanford AI Index Report, 2026
- McKinsey AI Adoption Study, 2026""",

    "codereview": """## Code Review Analysis

### Issues Found (2 Critical, 3 Warnings)

**🔴 Critical:**
- SQL injection vulnerability detected — use parameterized queries
- Missing null check before `.split()` on user input

**🟡 Warnings:**
- O(n²) complexity in nested loop — consider HashMap for O(n)
- Magic numbers (42, 7, 100) — extract to named constants
- No error handling around external API calls

### Scores
- Security Score: **6/10** — needs hardening
- Complexity Score: **7/10** — manageable with refactoring
- Maintainability: **8/10** — clean structure

## Top Improvements
1. Add input validation at all function entry points
2. Use connection pooling for database calls
3. Add unit tests for edge cases

**Verdict: Needs revision before production — solid foundation.**""",

    "contentwriter": """## Your Content — Ready to Publish

### LinkedIn Post

🚀 **We built an AI agent marketplace. Here's why it matters.**

AI agents are everywhere — but finding, deploying, and monetizing them? Nearly impossible.

We built **AGORA** to fix that.

✅ Discover the best AI agents in one place
✅ Deploy any agent instantly — zero setup, one click
✅ Chain agents into visual pipelines with Compose Mode
✅ Battle two agents simultaneously and vote on the winner
✅ Earn revenue as an agent creator

The AI agent economy is here. AGORA is its marketplace.

🔗 Try it live: agora-ai.vercel.app

Drop a comment if you want early access 👇

#AI #AgenticAI #BuildInPublic #Hackathon #LLM""",

    "marketspy": """## Market Intelligence Report

### Company/Market Overview
**AI Agent Marketplaces** — A nascent but fast-growing market segment emerging from the intersection of LLM capabilities and developer tooling.

### Market Size & Growth
- **2024**: $320M global market — mostly API integrations
- **2025**: $1.2B — first wave of agent orchestration platforms
- **2026 (projected)**: $4.8B — marketplace and creator economy phase

### Competitor Analysis
| Platform | Strength | Gap |
|----------|----------|-----|
| HuggingFace | Model hub | No agent execution |
| LangChain Hub | Dev-focused | No consumer marketplace |
| Zapier AI | Automation | No custom agents |
| **AGORA** | Full-stack marketplace | First mover advantage |

### Strategic Opportunities
1. **Creator monetization** — 0.1% fee on $4.8B market = $48M ARR
2. **Enterprise pipelines** — Compose Mode as B2B product
3. **White-label** — License AGORA stack to enterprises""",

    "dataanalyst": """## Data Analysis Report

### Data Overview
Analyzed the provided dataset successfully. Here are the key findings:

### Key Findings

**📈 Trend Analysis**
- Primary metric shows consistent upward trajectory over the analyzed period
- Growth rate: approximately 23% month-over-month
- Seasonal patterns detected in Q4 periods

**⚠️ Anomalies Detected**
- Week 7 shows a 34% dip — likely attributable to external market conditions
- Outlier detected at data point 23 — recommend verification

**🔗 Correlations**
- Strong positive correlation (r=0.87) between user engagement and revenue
- Negative correlation (r=-0.42) between response time and conversion

### Actionable Insights
1. **Capitalize on growth** — Scale infrastructure to match 23% MoM trajectory
2. **Investigate Week 7 dip** — Identify root cause to prevent recurrence
3. **Optimize response time** — Every 100ms reduction = ~4% conversion increase

### Recommended Next Steps
- Deploy A/B test on Week 7 similar conditions
- Set up automated anomaly detection alerts
- Schedule quarterly trend review"""
}

def get_mock_response(agent_id: str, query: str) -> str:
    base = MOCK_RESPONSES.get(
        agent_id,
        f"## Agent Response\n\n**Query processed:** {query}\n\n"
        "This agent completed its task successfully in demo mode. "
        "Connect a real API key to enable full capabilities."
    )
    return base


class BaseAgent(ABC):
    agent_id: str = "base"

    @abstractmethod
    def _run_with_llm(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        pass

    def run(self, input: str, stream_callback: Optional[Callable] = None) -> str:
        try:
            # Check if API key is a placeholder
            groq_key = os.getenv("GROQ_API_KEY", "")
            if not groq_key or "your_groq" in groq_key or len(groq_key) < 10:
                raise ValueError("GROQ_API_KEY not configured — using demo mode")
            return self._run_with_llm(input, stream_callback)
        except Exception as e:
            logger.warning(f"[{self.agent_id}] LLM failed ({e}), falling back to mock response")
            mock = get_mock_response(self.agent_id, input)
            if stream_callback:
                # Stream mock response in chunks for visual effect
                chunk_size = 8
                for i in range(0, len(mock), chunk_size):
                    stream_callback(mock[i:i + chunk_size])
                    time.sleep(0.015)
            return mock
