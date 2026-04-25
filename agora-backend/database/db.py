import aiosqlite
import os

DATABASE_URL = os.getenv("DATABASE_URL", "./agora.db")

async def get_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def init_db():
    from database.models import create_tables, seed_agents
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        await create_tables(db)
        await seed_agents(db)
        await db.commit()
