# AGORA — The Open AI Agent Marketplace 🚀

> **One Hub. Every AI Agent. Zero Barriers.**
> An autonomous AI ecosystem built for the future of agentic workflows.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-agora--ai.vercel.app-00F5FF?style=for-the-badge)](https://agora-frontend-sigma.vercel.app)
[![Backend Status](https://img.shields.io/badge/Backend-Live-00FF41?style=for-the-badge)](https://agora-backend-deployed.onrender.com/health)
[![HackIndia 2026](https://img.shields.io/badge/HackIndia%20×%20NIT%20Delhi-2026-7B2FBE?style=for-the-badge)](https://hackindia.xyz)

---

## 👥 Meet Team TechLions
*Winning the future of AI, one agent at a time.*

- **Team Leader:** [Shivam Singh](https://github.com/shivxmhere)
- **Core Developer:** Aditya Ojha
- **UI/UX & Design:** Prabhav Sagar
- **Intelligence & Strategy:** Shresta

---

## 🏗️ What is AGORA?

AGORA is a production-grade AI Agent Marketplace where developers **publish** autonomous agents and users **discover, deploy, and chain** them into complex pipelines. It solves the fragmentation of the AI economy by providing a unified interface for agentic execution.

### 🌟 Key Innovation Pillars
- **Curated Marketplace:** High-performance agents for Research, Analysis, Coding, and Content.
- **One-Click Deploy:** Instant execution with **real-time SSE (Server-Sent Events) streaming**.
- **Agent Compose:** A pipeline builder to chain multiple agents (e.g., *Research Agent* → *Content Writer*).
- **Battle Mode:** Head-to-head agent comparison (e.g., Llama vs. Mistral) with community voting.
- **High-Speed Intelligence:** Powered by **Groq LPU™ technology** delivering 300+ tokens/second.

---

## 🛠️ Technical Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Next.js 14 (App Router), Tailwind CSS, Framer Motion, Radix UI, Lucide Icons |
| **Backend** | FastAPI, Python 3.11, aiosqlite, Uvicorn |
| **AI Orchestration** | LangGraph, LangChain, Groq API (LLaMA 3.3 70B) |
| **Data & Search** | Tavily Web Search API, FAISS Vector Store, BeautifulSoup4 |
| **Deployment** | Vercel (Frontend), Render (Backend), GitHub Actions |

---

## ⚡ The 10-Agent Marketplace

| Agent | Capability | Tech Under the Hood |
|-------|------------|----------------------|
| **AutoResearch** | Deep Web Research | 5-Node LangGraph Pipeline + Tavily |
| **CyberSec** | Security Audits & CVEs | Live Vulnerability Intel + Groq |
| **DevOps** | Infrastructure & CI/CD | Best Practice Scaling Metrics |
| **UXResearcher** | User Personas & Heuristics| Feedback Synthesis + Design Empathy |
| **LegalTech** | Compliance Boilerplates | Real-time Precedents (Strict Disclaimers) |
| **Copywriter** | High-Converting SEO Copy | Viral Hooks & PAS Frameworks |
| **DataAnalyst** | Quantitative Insights | Structured File Upload Analysis (Text) |
| **MarketSpy** | Intelligence Reports | SWOT + Live Competitor Matrix |
| **CodeReview** | Software Auditing | Security & Complexity Scoring |
| **ContentWriter** | Creative Production | Multi-stage Creative Pipeline |

---

## 🚢 Deployment Overview

### Environment Setup
The project is fully configured for production. 
- **Frontend URL:** `https://agora-frontend-sigma.vercel.app`
- **Backend URL:** `https://agora-backend-deployed.onrender.com`

### Production Variables
Ensure the following are set in your deployment environment:
- `GROQ_API_KEY`: Extreme-speed LLM execution.
- `TAVILY_API_KEY`: Real-time web-aware research.
- `ENVIRONMENT`: `production`

---

## 🚀 Getting Started (Local Dev)

1. **Clone & Install**
   ```bash
   git clone https://github.com/shivxmhere/Agora.git
   ```

2. **Backend Setup**
   ```bash
   cd agora-backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd agora-frontend
   npm install
   npm run dev
   ```

---

*Built with ❤️ by Team TechLions for HackIndia × NIT Delhi 2026. AGORA is the marketplace for the autonomous age.*
