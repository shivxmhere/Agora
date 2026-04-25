# AGORA 🌐

**One hub. Every AI agent. Zero barriers.**

AGORA is an open, high-end marketplace for discovering, composing, and battling AI Agents. Built specifically for HackIndia × NIT Delhi 2026.

![Agora UI](https://via.placeholder.com/1200x600?text=AGORA+Marketplace)

### 🚀 Core Engineering Architecture
```text
[ CLIENT - Next.js 14 ]
       │  (Framer Motion, Tailwind, Recharts, SSE)
       ▼
 [ API GW - FastAPI ]  <-- REST & WebSocket
       │
   ┌───┴────────┬─────────────┐
   │            │             │
[ RUNNER ]  [ COMPOSE ]   [ BATTLE ]
(LangChain) (Sequential)  (Parallel)
   │            │             │
   ▼            ▼             ▼
[ TAVILY ]   [ GROQ / LLMs ] [ Local FAISS ]
```

### ✨ Unique Features
- **Agent Battle (/battle):** Run two LLM architectures or instructions purely in parallel via dynamic EventSources. Vote and compare outputs!
- **Agent Compose (/compose):** Chain together completely different entities programmatically (e.g., passing Research output directly into a Python Coder).
- **Creator Telemetry Dashboard (/dashboard):** Recharts-based statistics overview for top developers tracking agent execution popularity.
- **Terminal Execution UI:** Every run renders via real-time characters streams identical to a UNIX CLI utilizing `.onmessage` chunking safely.

### 💿 Quick Start
Ensure you have `Node.js 18+` and `Python 3.11+` installed.

1. **Clone & Setup Environment**
```bash
git clone https://github.com/shivxmhere/Agora.git
cd Agora
```

2. **Backend (FastAPI)**
```bash
cd agora-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env      # Add GROQ_API_KEY and TAVILY_API_KEY
uvicorn main:app --reload --port 8000
```

3. **Frontend (Next.js)**
```bash
cd ../agora-frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

### 🔑 Environment Variables
**Backend (`agora-backend/.env`)**
- `GROQ_API_KEY` = Your Groq Llama/Mixtral API base key.
- `TAVILY_API_KEY` = Web scraping key.
- `DATABASE_URL` = Optional. Defaults to local SQLite file `./agora.db`.

**Frontend (`agora-frontend/.env.local`)**
- `NEXT_PUBLIC_BACKEND_URL` = `http://localhost:8000` (Local) or your Railway deployment URL.

### 🌍 Deployment Instructions
- **Frontend:** Seamless deployment on **Vercel** configured via the native `vercel.json` already located in the `agora-frontend` folder. Point Vercel to `agora-frontend` as Root Directory.
- **Backend:** Seamless execution on **Railway** utilizing standard ASGI/Uvicorn config.
