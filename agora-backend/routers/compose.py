from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import asyncio
import uuid
import datetime
import json
from pydantic import BaseModel
from typing import List, Optional
from database.db import get_db
from agents.registry import registry

router = APIRouter(prefix="/api/compose", tags=["Compose"])

class StepConfig(BaseModel):
    agent_id: str

class ComposeRequest(BaseModel):
    steps: List[StepConfig]
    input: str
    session_id: str

class ComposeResponse(BaseModel):
    pipeline_run_id: str
    step_run_ids: List[str]

async def execute_pipeline(pipeline_run_id: str, request: ComposeRequest):
    import aiosqlite
    import os
    DATABASE_URL = os.getenv("DATABASE_URL", "./agora.db")
    
    db = await aiosqlite.connect(DATABASE_URL)
    current_input = request.input
    
    for i, step in enumerate(request.steps):
        agent_id = step.agent_id
        run_id = f"{pipeline_run_id}-step-{i}"
        
        # update status to running
        await db.execute("UPDATE agent_runs SET status = 'running' WHERE id = ?", (run_id,))
        await db.commit()
        
        start_time = datetime.datetime.utcnow()
        try:
            agent = registry.get_agent(agent_id)
            # Null callback since we aren't streaming
            def null_callback(x): pass
            output = await asyncio.to_thread(agent.run, current_input, null_callback)
            
            end_time = datetime.datetime.utcnow()
            run_time = (end_time - start_time).total_seconds()
            
            now = datetime.datetime.utcnow().isoformat()
            await db.execute('''
                UPDATE agent_runs 
                SET status = 'completed', output = ?, completed_at = ?, run_time = ?
                WHERE id = ?
            ''', (output, now, run_time, run_id))
            await db.commit()
            
            # Output becomes next input
            current_input = output
            
        except Exception as e:
            now = datetime.datetime.utcnow().isoformat()
            await db.execute('''
                UPDATE agent_runs 
                SET status = 'failed', output = ?, completed_at = ?
                WHERE id = ?
            ''', (str(e), now, run_id))
            await db.commit()
            break
            
    await db.close()


@router.post("/run", response_model=ComposeResponse)
async def create_compose_run(request: ComposeRequest, background_tasks: BackgroundTasks, db = Depends(get_db)):
    pipeline_run_id = str(uuid.uuid4())
    step_run_ids = []
    
    now = datetime.datetime.utcnow().isoformat()
    
    for i, step in enumerate(request.steps):
        # find agent
        cursor = await db.execute("SELECT * FROM agents WHERE id = ? OR slug = ?", (step.agent_id, step.agent_id))
        agent_row = await cursor.fetchone()
        
        if not agent_row:
            raise HTTPException(status_code=404, detail=f"Agent '{step.agent_id}' not found")
        
        real_agent_id = dict(agent_row)["id"]
        request.steps[i].agent_id = real_agent_id # use real ID
        
        step_run_id = f"{pipeline_run_id}-step-{i}"
        step_run_ids.append(step_run_id)
        
        await db.execute('''
            INSERT INTO agent_runs (id, agent_id, session_id, input, status, started_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (step_run_id, real_agent_id, request.session_id, request.input if i == 0 else 'Waiting for previous output...', 'queued', now))
        
    await db.commit()
    
    background_tasks.add_task(execute_pipeline, pipeline_run_id, request)
    
    return {
        "pipeline_run_id": pipeline_run_id,
        "step_run_ids": step_run_ids
    }
