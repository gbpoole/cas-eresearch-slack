# project/app/main.py

from fastapi import FastAPI, Depends
from app.config import get_settings, Settings
from slackers.server import router


app = FastAPI()
app.include_router(router, prefix='/slack')


@app.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing
    }
