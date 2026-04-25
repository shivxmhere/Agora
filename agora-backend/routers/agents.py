from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import uuid
import datetime
import json
from database.db import get_db
from schemas.schemas import AgentCard, AgentDetail, AgentCreate

router = APIRouter(prefix="/api/agents", tags=["Agents"])

@router.get("", response_model=List[AgentCard])
async def list_agents(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = Query("newest", pattern="^(rating|runs|newest)$"),
    db = Depends(get_db)
):
    query = "SELECT * FROM agents WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
        
    if search:
        query += " AND (name LIKE ? OR tags LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
        
    if sort == "rating":
        query += " ORDER BY rating DESC"
    elif sort == "runs":
        query += " ORDER BY total_runs DESC"
    else:
        query += " ORDER BY created_at DESC"
        
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    
    agents = []
    for row in rows:
        agent_dict = dict(row)
        agent_dict['tags'] = json.loads(agent_dict['tags']) if agent_dict['tags'] else []
        agents.append(agent_dict)
        
    return agents

@router.get("/{agent_id}", response_model=AgentDetail)
async def get_agent(agent_id: str, db = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    agent_dict = dict(row)
    agent_dict['tags'] = json.loads(agent_dict['tags']) if agent_dict['tags'] else []
    agent_dict['capabilities'] = json.loads(agent_dict['capabilities']) if agent_dict['capabilities'] else []
    return agent_dict

@router.post("", response_model=AgentCard)
async def create_agent(agent: AgentCreate, db = Depends(get_db)):
    # Generate ID and Slug
    agent_id = str(uuid.uuid4())
    slug = agent.name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8]
    now = datetime.datetime.utcnow().isoformat()
    
    await db.execute('''
        INSERT INTO agents (
            id, name, slug, tagline, description, long_description, category, 
            tags, creator_name, capabilities, input_placeholder, created_at,
            rating, total_runs, creator_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0, 0.0)
    ''', (
        agent_id, agent.name, slug, agent.tagline, agent.description, agent.long_description, agent.category,
        json.dumps(agent.tags), agent.creator_name, json.dumps(agent.capabilities), agent.input_placeholder, now
    ))
    await db.commit()
    
    cursor = await db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    row = await cursor.fetchone()
    agent_dict = dict(row)
    agent_dict['tags'] = json.loads(agent_dict['tags'])
    return agent_dict

@router.post("/{agent_id}", response_model=AgentDetail)
async def update_agent(agent_id: str, agent: AgentCreate, db = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Agent not found")
        
    await db.execute('''
        UPDATE agents 
        SET name=?, tagline=?, description=?, long_description=?, category=?, 
            tags=?, creator_name=?, capabilities=?, input_placeholder=?
        WHERE id=?
    ''', (
        agent.name, agent.tagline, agent.description, agent.long_description, agent.category,
        json.dumps(agent.tags), agent.creator_name, json.dumps(agent.capabilities), agent.input_placeholder, agent_id
    ))
    await db.commit()
    
    cursor = await db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    row = await cursor.fetchone()
    agent_dict = dict(row)
    agent_dict['tags'] = json.loads(agent_dict['tags']) if agent_dict['tags'] else []
    agent_dict['capabilities'] = json.loads(agent_dict['capabilities']) if agent_dict['capabilities'] else []
    return agent_dict
