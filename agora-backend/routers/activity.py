from fastapi import APIRouter, Depends
from typing import List
from database.db import get_db
from schemas.schemas import ActivityLog

router = APIRouter(prefix="/api/activity", tags=["Activity"])

from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

@router.get("/feed", response_model=List[ActivityLog])
async def get_activity_feed(db = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 20")
    rows = await cursor.fetchall()
    
    feed = []
    import datetime
    
    def get_time_ago(dt_str: str) -> str:
        try:
            dt = datetime.datetime.fromisoformat(dt_str)
            now = datetime.datetime.utcnow()
            diff = (now - dt).total_seconds()
            if diff < 60:
                return f"{int(diff)}s ago"
            elif diff < 3600:
                return f"{int(diff//60)}m ago"
            elif diff < 86400:
                return f"{int(diff//3600)}h ago"
            else:
                return f"{int(diff//86400)}d ago"
        except:
            return "just now"
            
    for row in rows:
        feed.append({
            "agent_name": row["agent_name"],
            "action": row["action"],
            "location": row["location"],
            "time": get_time_ago(row["created_at"])
        })
        
    return feed
