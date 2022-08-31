from fastapi import FastAPI, Depends
from slackers.server import router, commands
import logging

import app.config as config
import app.actions as actions
import app.coda as coda
import app.commands as commands
import app.config as config
import app.error as error
import app.events as events
import app.interactive as interactive
import app.slack as slack

log = logging.getLogger(__name__)

app = FastAPI()
app.include_router(router, prefix='/slack')

@app.get("/ping")
async def pong(settings: config.Settings = Depends(config.get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing
    }
