import redis.asyncio as aioredis

from contextlib import asynccontextmanager
from fastapi import FastAPI
from os import getenv

from .routes import (
    courses_router,
    studio_router,
    training_info_router,
    trips_router,
    group_training_router,
    videos_router,
    auth_router,
    users_router,
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    ...

app = FastAPI()

app.include_router(courses_router)
app.include_router(studio_router)
app.include_router(training_info_router)
app.include_router(trips_router)
app.include_router(group_training_router)
app.include_router(trips_router)
app.include_router(videos_router)
app.include_router(auth_router)
app.include_router(users_router)
