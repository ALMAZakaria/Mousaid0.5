import asyncpg
from backend.config import settings
import logging

db_pool = None
logger = logging.getLogger(__name__)

def get_db_pool():
    global db_pool
    if db_pool is None:
        raise RuntimeError("Database pool is not initialized!")
    return db_pool

async def startup():
    global db_pool
    db_pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL, min_size=1, max_size=10)

async def shutdown():
    global db_pool
    if db_pool is not None:
        await db_pool.close()

async def get_conversation_history(session_id: str, limit: int = 20):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT role, content, timestamp FROM conversation_logs
            WHERE session_id = $1
            ORDER BY timestamp DESC LIMIT $2
            """, session_id, limit
        )
        return [dict(row) for row in reversed(rows)]

async def add_to_history(session_id: str, role: str, content: str):
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO conversation_logs (session_id, role, content, timestamp)
            VALUES ($1, $2, $3, NOW())
            """, session_id, role, content
        ) 