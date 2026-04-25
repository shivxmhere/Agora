from fastapi import APIRouter, Depends, HTTPException
import uuid
import datetime
from database.db import get_db
from schemas.schemas import RatingCreate

router = APIRouter(prefix="/api/agents", tags=["Ratings"])

@router.post("/{agent_id}/rate")
async def rate_agent(agent_id: str, rating_data: RatingCreate, db = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    agent_row = await cursor.fetchone()
    if not agent_row:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    rating_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat()
    
    await db.execute('''
        INSERT INTO ratings (id, agent_id, session_id, stars, review, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (rating_id, agent_id, rating_data.session_id, rating_data.stars, rating_data.review, now))
    
    # Update average rating
    cursor = await db.execute("SELECT AVG(stars) as avg_stars FROM ratings WHERE agent_id = ?", (agent_id,))
    avg_row = await cursor.fetchone()
    new_avg = round(avg_row["avg_stars"], 1) if avg_row["avg_stars"] else rating_data.stars
    
    await db.execute("UPDATE agents SET rating = ? WHERE id = ?", (new_avg, agent_id))
    
    # Broadcast activity log
    agent_name = dict(agent_row)["name"]
    action_text = f'rated {rating_data.stars} stars'
    await db.execute('''
        INSERT INTO activity_log (id, agent_id, agent_name, action, location, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), agent_id, agent_name, action_text, 'Global', now))
    
    await db.commit()
    
    # Broadcast to websockets
    from routers.activity import manager
    import asyncio
    asyncio.create_task(manager.broadcast({
        "agent_name": agent_name,
        "action": action_text,
        "location": "Global",
        "time": "just now"
    }))
    
    return {"rating": new_avg}
