import hashlib
import redis.asyncio as redis

# Connection pool setup
redis_pool = redis.ConnectionPool.from_url(
    "redis://localhost:6379", decode_responses=True
)


async def get_redis():
    """Dependency provider for FastAPI routes."""
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.close()


async def get_cache_key(prompt: str) -> str:
    """Computes a deterministic SHA256 key for Redis caching."""
    hashed_prompt = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return f"ai_cache:{hashed_prompt}"
