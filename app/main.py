from fastapi import FastAPI

from .routes import courses_router, studio_router, group_training_router, trips_router

app = FastAPI()

app.include_router(courses_router)
app.include_router(studio_router)
app.include_router(group_training_router)
app.include_router(trips_router)
