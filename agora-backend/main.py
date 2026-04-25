import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database.db import init_db, seed_agents_if_empty, seed_activity_if_empty

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AGORA backend...")
    await init_db()
    await seed_agents_if_empty()
    await seed_activity_if_empty()
    logger.info("AGORA backend ready.")
    yield
    logger.info("AGORA backend shutting down.")

app = FastAPI(
    title="AGORA API",
    description="The Open AI Agent Marketplace",
    version="1.0.0",
    lifespan=lifespan
)

# CRITICAL: allow_credentials MUST be False when allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

from routers import agents, runner, ratings, activity, analytics, compose
app.include_router(agents.router)
app.include_router(runner.router)
app.include_router(ratings.router)
app.include_router(activity.router)
app.include_router(analytics.router)
app.include_router(compose.router)

@app.get("/health")
async def health():
    from database.db import get_agent_count, get_today_run_count
    try:
        return {
            "status": "live",
            "service": "AGORA API",
            "agents": await get_agent_count(),
            "runs_today": await get_today_run_count()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"message": "AGORA API is live", "docs": "/docs", "health": "/health"}

@app.websocket("/ws/activity")
async def websocket_activity(websocket: WebSocket):
    from routers.activity import manager
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
