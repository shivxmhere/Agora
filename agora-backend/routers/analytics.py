from fastapi import APIRouter, Depends, HTTPException
from database.db import get_db
from schemas.schemas import AnalyticsResponse
import datetime

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/{creator_name}", response_model=AnalyticsResponse)
async def get_analytics(creator_name: str, db = Depends(get_db)):
    # Get all agents by creator
    cursor = await db.execute("SELECT * FROM agents WHERE creator_name = ?", (creator_name,))
    agents = await cursor.fetchall()
    
    if not agents:
        raise HTTPException(status_code=404, detail="No agents found for this creator")
        
    total_runs = sum([a["total_runs"] for a in agents])
    total_earnings = total_runs * 0.001
    avg_rating = sum([a["rating"] for a in agents]) / len(agents) if agents else 0
    top_agent = max(agents, key=lambda a: a["total_runs"])["name"] if agents else "N/A"
    
    runs_by_agent = {a["name"]: a["total_runs"] for a in agents}
    
    # Mock data for past 7 days based on total runs
    runs_by_day = {}
    now = datetime.datetime.utcnow()
    remaining_runs = total_runs
    
    for i in range(6, 0, -1):
        day = (now - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        daily_runs = int(total_runs / 7)
        runs_by_day[day] = daily_runs
        remaining_runs -= daily_runs
        
    runs_by_day[now.strftime("%Y-%m-%d")] = remaining_runs
    
    return {
        "total_runs": total_runs,
        "total_earnings": total_earnings,
        "avg_rating": round(avg_rating, 2),
        "top_agent": top_agent,
        "runs_by_day": runs_by_day,
        "runs_by_agent": runs_by_agent
    }
