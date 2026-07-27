from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings


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
from .utils import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis(app)
    yield
    await close_redis(app)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses_router)
app.include_router(studio_router)
app.include_router(training_info_router)
app.include_router(trips_router)
app.include_router(group_training_router)
app.include_router(videos_router)
app.include_router(auth_router)
app.include_router(users_router)
