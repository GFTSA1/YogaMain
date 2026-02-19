import uvicorn

from fastapi import FastAPI

from .routes import courses_router

app = FastAPI()

app.include_router(courses_router)

if __name__ == "__main__":
    uvicorn.run(app, reload=True)
