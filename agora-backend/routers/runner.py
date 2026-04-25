from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
import asyncio
import uuid
import datetime
from database.db import get_db
from schemas.schemas import RunCreate, RunResponse, RunStatusResponse
from agents.registry import registry

router = APIRouter(prefix="/api", tags=["Runner"])

@router.post("/agents/{agent_id}/run", response_model=RunResponse)
async def create_run(agent_id: str, run_data: RunCreate, db = Depends(get_db)):
    # verify agent exists
    cursor = await db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    agent_row = await cursor.fetchone()
    if not agent_row:
        raise HTTPException(status_code=404, detail="Agent not found")

    run_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat()

    await db.execute('''
        INSERT INTO agent_runs (id, agent_id, session_id, input, status, started_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (run_id, agent_id, run_data.session_id, run_data.input, 'queued', now))
    
    # Broadcast activity log
    agent_name = dict(agent_row)["name"]
    await db.execute('''
        INSERT INTO activity_log (id, agent_id, agent_name, action, location, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), agent_id, agent_name, 'just ran', 'Global', now))
    await db.commit()
    
    # Broadcast to websockets
    from routers.activity import manager
    asyncio.create_task(manager.broadcast({
        "agent_name": agent_name,
        "action": "just ran",
        "location": "Global",
        "time": "just now"
    }))
    
    return {"run_id": run_id, "stream_url": f"/api/runs/{run_id}/stream"}

async def agent_stream_generator(run_id: str, agent_id: str, run_input: str, request: Request):
    import aiosqlite
    import os
    DATABASE_URL = os.getenv("DATABASE_URL", "./agora.db")
    
    try:
        agent = registry.get_agent(agent_id)
        
        queue = asyncio.Queue()
        
        def stream_callback(content: str):
            asyncio.run_coroutine_threadsafe(queue.put(content), asyncio.get_event_loop())
            
        async def run_agent_coro():
            start_time = datetime.datetime.utcnow()
            try:
                # Need to use to_thread because LangChain block
                output = await asyncio.to_thread(agent.run, run_input, stream_callback)
                
                # Signal completion
                end_time = datetime.datetime.utcnow()
                run_time = (end_time - start_time).total_seconds()
                await queue.put({"type": "done", "run_time": run_time, "output": output})
            except Exception as e:
                await queue.put({"type": "error", "message": str(e)})

        task = asyncio.create_task(run_agent_coro())
        
        db = await aiosqlite.connect(DATABASE_URL)
        await db.execute("UPDATE agent_runs SET status = 'running' WHERE id = ?", (run_id,))
        await db.commit()

        # Stream content
        final_output = ""
        final_run_time = 0.0
        
        while True:
            if await request.is_disconnected():
                task.cancel()
                break
                
            item = await queue.get()
            
            if isinstance(item, dict):
                if item["type"] == "done":
                    final_output = item["output"]
                    final_run_time = item["run_time"]
                    import json
                    yield f"data: {json.dumps({'type': 'done', 'run_time': final_run_time})}\n\n"
                    break
                elif item["type"] == "error":
                    import json
                    yield f"data: {json.dumps({'type': 'error', 'message': item['message']})}\n\n"
                    
                    await db.execute("UPDATE agent_runs SET status = 'failed' WHERE id = ?", (run_id,))
                    await db.commit()
                    await db.close()
                    return
            else:
                import json
                yield f"data: {json.dumps({'type': 'token', 'content': item})}\n\n"

        # Update DB on complete
        if final_output:
            now = datetime.datetime.utcnow().isoformat()
            await db.execute('''
                UPDATE agent_runs 
                SET status = 'completed', output = ?, completed_at = ?, run_time = ?
                WHERE id = ?
            ''', (final_output, now, final_run_time, run_id))
            
            # Increment agent run count
            await db.execute('''
                UPDATE agents 
                SET total_runs = total_runs + 1 
                WHERE id = ?
            ''', (agent_id,))
            
            await db.commit()
        
        await db.close()
        
    except Exception as e:
        import json
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@router.get("/runs/{run_id}/stream")
async def stream_run(run_id: str, request: Request, db = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM agent_runs WHERE id = ?", (run_id,))
    run = await cursor.fetchone()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    agent_id = run["agent_id"]
    run_input = run["input"]

    return StreamingResponse(
        agent_stream_generator(run_id, agent_id, run_input, request), 
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

@router.get("/runs/{run_id}", response_model=RunStatusResponse)
async def get_run(run_id: str, db = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM agent_runs WHERE id = ?", (run_id,))
    run = await cursor.fetchone()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    return {
        "status": run["status"],
        "output": run["output"],
        "run_time": run["run_time"]
    }
