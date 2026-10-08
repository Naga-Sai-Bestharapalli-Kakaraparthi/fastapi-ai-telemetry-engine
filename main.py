import asyncio
import json
import time
from fastapi import Depends, FastAPI, HTTPException, Response, status
from redis.asyncio import Redis

from redis_client import get_cache_key, get_redis
from schemas import PromptPayload, TaskResponse

app = FastAPI(
    title="Async Python FastAPI AI Telemetry Engine",
    version="1.0.0",
    description="High-throughput AI task ingestion engine using Redis Cache-Aside and Pydantic validation.",
)


async def simulate_ai_inference(prompt: str) -> str:
    """Simulates LLM inference delay (300ms network overhead)."""
    await asyncio.sleep(0.3)
    return f"Processed telemetry insights for: '{prompt}'"


@app.post(
    "/api/v1/analyze",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_task(
    payload: PromptPayload,
    response: Response,
    r: Redis = Depends(get_redis),
):
    start_time = time.perf_counter()

    try:
        cache_key = await get_cache_key(payload.prompt)
        cached_result = await r.get(cache_key)

        # Cache Hit Path (<20ms target)
        if cached_result:
            latency = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Cache-Status"] = "HIT"
            response.headers["X-Response-Time-MS"] = str(latency)

            return TaskResponse(
                status="success",
                source="redis_cache",
                prompt=payload.prompt,
                result=cached_result,
                latency_ms=latency,
            )

        # Cache Miss Path (AI API Processing)
        ai_output = await simulate_ai_inference(payload.prompt)

        # Set cache with 1-hour TTL (3600 seconds)
        await r.setex(cache_key, 3600, ai_output)

        latency = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Cache-Status"] = "MISS"
        response.headers["X-Response-Time-MS"] = str(latency)

        return TaskResponse(
            status="success",
            source="ai_engine",
            prompt=payload.prompt,
            result=ai_output,
            latency_ms=latency,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline Processing Error: {str(e)}",
        )
