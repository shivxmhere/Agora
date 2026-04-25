import asyncio
import json
import uuid
import time
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from database.db import get_run, create_run, update_run, log_activity
from agents.registry import get_agent, AGENT_MAP

router = APIRouter(prefix="/api", tags=["Runner"])
logger = logging.getLogger(__name__)


class RunRequest(BaseModel):
    input: str
    session_id: str = None


@router.post("/agents/{agent_id}/run")
async def start_run(agent_id: str, body: RunRequest):
    if agent_id not in AGENT_MAP:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    if not body.input or not body.input.strip():
        raise HTTPException(status_code=422, detail="Input cannot be empty")

    run_id = str(uuid.uuid4())
    session_id = body.session_id or str(uuid.uuid4())

    await create_run(run_id, agent_id, session_id, body.input.strip())
    logger.info(f"Run created: {run_id} for agent: {agent_id}")

    # Broadcast to websocket activity feed
    try:
        from routers.activity import manager
        asyncio.create_task(manager.broadcast({
            "agent_name": agent_id,
            "action": "just ran",
            "location": "Global",
            "time": "just now"
        }))
    except Exception:
        pass

    return {
        "run_id": run_id,
        "agent_id": agent_id,
        "status": "queued",
        "stream_url": f"/api/runs/{run_id}/stream"
    }


@router.get("/runs/{run_id}/stream")
async def stream_run(run_id: str):
    run = await get_run(run_id)
    if not run:
        async def error_gen():
            yield f"data: {json.dumps({'type': 'error', 'message': 'Run not found'})}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")

    async def generate():
        tokens = []
        done_event = asyncio.Event()
        start_time = time.time()

        def stream_callback(content: str):
            if content:
                tokens.append(content)

        await update_run(run_id, status="running")

        # Keepalive so browser doesn't timeout before first token
        yield f"data: {json.dumps({'type': 'status', 'message': 'Agent starting...'})}\n\n"

        async def run_agent():
            try:
                agent = get_agent(run["agent_id"])
                result = await asyncio.to_thread(
                    agent.run, run["input"], stream_callback
                )
                elapsed = round(time.time() - start_time, 2)
                await update_run(run_id, status="completed", output=result, run_time=elapsed)
            except Exception as e:
                logger.error(f"Agent run error for {run_id}: {e}", exc_info=True)
                tokens.append(f"\n\n❌ **Error:** {str(e)}")
                await update_run(run_id, status="failed", output=str(e))
            finally:
                done_event.set()

        agent_task = asyncio.create_task(run_agent())

        # Poll and stream tokens
        sent_index = 0
        while not done_event.is_set() or sent_index < len(tokens):
            while sent_index < len(tokens):
                yield f"data: {json.dumps({'type': 'token', 'content': tokens[sent_index]})}\n\n"
                sent_index += 1
            if not done_event.is_set():
                await asyncio.sleep(0.05)

        # Drain any remaining tokens
        while sent_index < len(tokens):
            yield f"data: {json.dumps({'type': 'token', 'content': tokens[sent_index]})}\n\n"
            sent_index += 1

        run_time = round(time.time() - start_time, 2)
        yield f"data: {json.dumps({'type': 'done', 'run_time': run_time, 'run_id': run_id})}\n\n"

        await agent_task  # clean up

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/runs/{run_id}")
async def get_run_status(run_id: str):
    run = await get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
