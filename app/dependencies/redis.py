import redis.asyncio as aioredis

from fastapi import Depends
from typing import Annotated
from redis.asyncio import Redis

from app.utils import get_redis

RedisDep = Annotated[Redis, Depends(get_redis)]
