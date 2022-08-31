from fastapi import FastAPI, Depends
from app.config import Settings, get_settings, init_slack, init_coda
from slackers.server import router, commands
import logging

import app.actions
import app.coda
import app.commands
import app.config
import app.error
import app.events
import app.interactive
import app.slack

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger(__name__)

app = FastAPI()
app.include_router(router, prefix='/slack')

@app.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing
    }
