# AGORA — The Open AI Agent Marketplace

> **One hub. Every AI agent. Zero barriers.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-agora--ai.vercel.app-00F5FF?style=for-the-badge)](https://agora-ai.vercel.app)
[![HackIndia 2026](https://img.shields.io/badge/HackIndia%20×%20NIT%20Delhi-2026-7B2FBE?style=for-the-badge)](https://hackindia.xyz)

**Team:** TechLions · Shivam Singh · Aditya Ojha · Ankur Verma

---

## What is AGORA?

AGORA is a full-stack AI agent marketplace where developers **publish** autonomous AI agents and users **discover, deploy, and compose** them — with zero setup required.

AGORA is the **first platform** that combines:
- A **curated marketplace** for browsing AI agents
- **One-click execution** with real-time streaming output
- **Compose Mode** — chain agents into visual pipelines
- **Battle Mode** — run two agents simultaneously and vote on the winner
- A **Creator Economy** with usage analytics and revenue dashboards

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🏪 **Marketplace** | Browse 5+ agents by category, rating, use case |
| ⚡ **One-Click Deploy** | Run any agent with SSE real-time streaming |
| 🔗 **Agent Compose** | Chain agents into multi-step pipelines |
| ⚔️ **Battle Mode** | Side-by-side agent comparison with voting |
| 📊 **Creator Dashboard** | Analytics, run counts, earnings tracking |
| 🌐 **Live Activity Feed** | Real-time global agent usage WebSocket stream |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Vercel)                │
│   Next.js 14 · TypeScript · Tailwind    │
│   Framer Motion · SWR · Recharts        │
└──────────────┬──────────────────────────┘
               │ REST + SSE + WebSocket
┌──────────────▼──────────────────────────┐
│         Backend (Railway)                │
│   FastAPI · Python 3.11 · aiosqlite     │
│   SSE-Starlette · WebSockets            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         AI Layer                         │
│   LangGraph Pipelines                   │
│   Groq LLaMA 3.3 70B (300 tok/s)       │
│   Tavily Web Search                     │
│   FAISS Vector Store                    │
└─────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Free API keys: [Groq](https://console.groq.com) · [Tavily](https://app.tavily.com)

### Backend
```bash
cd agora-backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env: add GROQ_API_KEY and TAVILY_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd agora-frontend
npm install
# Edit .env.local: set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev
```

Open **http://localhost:3000** — the API health check is at **http://localhost:8000/health**

---

## 🔑 Environment Variables

### Backend (`agora-backend/.env`)
```env
GROQ_API_KEY=gsk_...          # console.groq.com (free tier)
TAVILY_API_KEY=tvly-...       # app.tavily.com (free tier)
DATABASE_URL=./agora.db       # SQLite path
ENVIRONMENT=production
```

### Frontend (`agora-frontend/.env.local`)
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
# In production: https://your-railway-url.up.railway.app
```

---

## 🚢 Deployment

### Backend → Railway
1. New Project → Deploy from GitHub → select `agora-backend` folder
2. Add env vars: `GROQ_API_KEY`, `TAVILY_API_KEY`, `DATABASE_URL=./agora.db`
3. Railway auto-detects `nixpacks.toml` and `Procfile`
4. Settings → Networking → Generate Domain → copy URL

### Frontend → Vercel
1. New Project → Import GitHub → select `agora-frontend` folder
2. Add env var: `NEXT_PUBLIC_BACKEND_URL=https://your-railway-url.up.railway.app`
3. Deploy — Vercel auto-detects Next.js

### Verification Checklist
- ✅ `https://[railway]/health` → `{"status":"live","agents":5}`
- ✅ `https://[railway]/api/agents` → array of 5 agents
- ✅ `https://[vercel]/` → homepage with agents
- ✅ `https://[vercel]/marketplace` → agent grid
- ✅ `https://[vercel]/battle` → side-by-side execution
- ✅ `https://[vercel]/compose` → pipeline builder

---

## 🤖 Agents

| Agent | Category | Type | Speed |
|-------|----------|------|-------|
| AutoResearch | Research | LangGraph 5-node pipeline | ~78s |
| CodeReview | Developer Tools | Single LLM + structured prompt | ~22s |
| ContentWriter | Creative | 3-stage pipeline | ~35s |
| MarketSpy | Business | Single LLM + analysis | ~30s |
| DataAnalyst | Analytics | Single LLM + structured insights | ~25s |

> **Demo Mode:** All agents automatically fall back to high-quality mock responses if API keys are not configured — zero crashes guaranteed.

---

*Built with ❤️ for HackIndia × NIT Delhi 2026 — AI Agents Marketplace Track*
