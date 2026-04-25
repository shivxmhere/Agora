from fastapi import APIRouter, Depends, HTTPException
from database.db import get_db
import datetime
import json

router = APIRouter(prefix="/api", tags=["Analytics by Creator"])

@router.get("/analytics/{creator_name}")
async def get_analytics(creator_name: str, db = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM agents WHERE creator_name = ?", (creator_name,))
    agents = await cursor.fetchall()
    
    if not agents:
        return {
            "total_runs": 0, "avg_rating": 0, "total_earned": 0, "agents_live": 0,
            "top_agent": {"name": "None", "total_runs": 0}, "runs_by_day": [],
            "runs_by_agent": [], "recent_runs": []
        }
        
    total_runs = sum([a["total_runs"] for a in agents])
    total_earned = total_runs * 0.001
    avg_rating = sum([a["rating"] for a in agents]) / len(agents) if agents else 0
    top_agent = max(agents, key=lambda a: a["total_runs"]) if agents else None
    
    runs_by_agent = [{"agent_name": a["name"], "runs": a["total_runs"]} for a in agents]
    
    # Mock data for past 7 days based on total runs
    runs_by_day = []
    now = datetime.datetime.utcnow()
    remaining_runs = total_runs
    
    for i in range(6, 0, -1):
        day = (now - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        daily_runs = int(total_runs / 7)
        runs_by_day.append({"date": day, "runs": daily_runs})
        remaining_runs -= daily_runs
        
    runs_by_day.append({"date": now.strftime("%Y-%m-%d"), "runs": remaining_runs})
    
    # recent runs (mocked for now, as we don't have run_logs table linked to agents yet)
    recent_runs = []
    if top_agent:
        recent_runs = [
            {"agent_name": top_agent["name"], "input_preview": "Analyze market trends...", "status": "completed", "created_at": "10 mins ago"},
            {"agent_name": top_agent["name"], "input_preview": "Generate python script...", "status": "completed", "created_at": "2 hours ago"},
        ]
    
    return {
        "total_runs": total_runs,
        "avg_rating": round(avg_rating, 2),
        "total_earned": round(total_earned, 2),
        "agents_live": len([a for a in agents if a["status"] == "live"]),
        "top_agent": {"name": top_agent["name"], "total_runs": top_agent["total_runs"]} if top_agent else {"name": "None", "total_runs": 0},
        "runs_by_day": runs_by_day,
        "runs_by_agent": runs_by_agent,
        "recent_runs": recent_runs
    }

@router.get("/creators/leaderboard")
async def get_leaderboard(db = Depends(get_db)):
    cursor = await db.execute("""
        SELECT creator_name, MAX(creator_score) as creator_score, 
               COUNT(id) as total_agents, SUM(total_runs) as total_runs, 
               AVG(rating) as avg_rating
        FROM agents 
        GROUP BY creator_name 
        ORDER BY total_runs DESC 
        LIMIT 5
    """)
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]
