from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.db import init_db
from routers import agents, runner, ratings, activity, analytics, compose
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB and seed demo agents
    await init_db()
    yield

app = FastAPI(title="AGORA Backend", lifespan=lifespan)

# CORS enabled for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router)
app.include_router(runner.router)
app.include_router(ratings.router)
app.include_router(activity.router)
app.include_router(analytics.router)
app.include_router(compose.router)

@app.get("/health")
async def health_check():
    import aiosqlite
    import os
    DATABASE_URL = os.getenv("DATABASE_URL", "./agora.db")
    try:
        async with aiosqlite.connect(DATABASE_URL) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM agents")
            row = await cursor.fetchone()
            num_agents = row[0] if row else 0
            
            cursor = await db.execute("SELECT COUNT(*) FROM agent_runs")
            row = await cursor.fetchone()
            runs_today = row[0] if row else 0
            
        return {"status": "live", "agents": num_agents, "runs_today": runs_today}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws/activity")
async def websocket_activity(websocket: WebSocket):
    from routers.activity import manager
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
