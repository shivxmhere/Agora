from fastapi import APIRouter, HTTPException, BackgroundTasks
import asyncio
import uuid
import json
import logging
from datetime import datetime
from pydantic import BaseModel
from typing import List
from database.db import get_run, update_run
from agents.registry import get_agent, AGENT_MAP

router = APIRouter(prefix="/api/compose", tags=["Compose"])
logger = logging.getLogger(__name__)


class StepConfig(BaseModel):
    agent_id: str


class ComposeRequest(BaseModel):
    steps: List[StepConfig]
    input: str
    session_id: str = None


async def execute_pipeline(pipeline_run_id: str, steps: List[str], initial_input: str):
    """Sequentially execute pipeline steps, passing output of each as input to next."""
    import aiosqlite
    import os
    DB_PATH = os.getenv("DATABASE_URL", "./agora.db")

    current_input = initial_input
    for i, agent_id in enumerate(steps):
        run_id = f"{pipeline_run_id}-step-{i}"
        await update_run(run_id, status="running")
        start = datetime.utcnow()
        try:
            agent = get_agent(agent_id)
            output = await asyncio.to_thread(agent.run, current_input, None)
            run_time = (datetime.utcnow() - start).total_seconds()
            await update_run(run_id, status="completed", output=output, run_time=run_time)
            current_input = output  # chain output → next input
        except Exception as e:
            logger.error(f"Pipeline step {i} failed: {e}")
            await update_run(run_id, status="failed", output=str(e))
            break  # stop pipeline on failure


@router.post("/run")
async def create_compose_run(request: ComposeRequest, background_tasks: BackgroundTasks):
    if not request.steps:
        raise HTTPException(status_code=422, detail="At least one step required")

    # Validate agents exist
    for step in request.steps:
        if step.agent_id not in AGENT_MAP:
            raise HTTPException(status_code=404, detail=f"Agent '{step.agent_id}' not found")

    pipeline_run_id = str(uuid.uuid4())
    session_id = request.session_id or str(uuid.uuid4())
    step_run_ids = []
    now = datetime.utcnow().isoformat()

    import aiosqlite
    import os
    DB_PATH = os.getenv("DATABASE_URL", "./agora.db")

    async with aiosqlite.connect(DB_PATH) as db:
        for i, step in enumerate(request.steps):
            step_run_id = f"{pipeline_run_id}-step-{i}"
            step_run_ids.append(step_run_id)
            input_text = request.input if i == 0 else "Waiting for previous step..."
            await db.execute("""
                INSERT INTO agent_runs (id, agent_id, session_id, input, status, started_at)
                VALUES (?, ?, ?, ?, 'queued', ?)
            """, (step_run_id, step.agent_id, session_id, input_text, now))
        await db.commit()

    agent_ids = [s.agent_id for s in request.steps]
    background_tasks.add_task(execute_pipeline, pipeline_run_id, agent_ids, request.input)

    return {"pipeline_run_id": pipeline_run_id, "step_run_ids": step_run_ids}
