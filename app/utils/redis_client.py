import redis.asyncio as aioredis
from fastapi import Request
from ..settings import settings


async def init_redis(app) -> None:
    app.state.redis = aioredis.from_url(
        str(settings.redis_url),
        encoding="utf-8",
        decode_responses=True,
    )
    await app.state.redis.ping()


async def close_redis(app) -> None:
    if getattr(app.state, "redis", None) is not None:
        await app.state.redis.close()


def get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis
