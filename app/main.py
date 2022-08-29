# project/app/main.py

from fastapi import FastAPI, Depends
from app.config import Settings, get_settings, init_slack, init_coda
from slackers.server import router, commands
import logging

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

@commands.on("time")  # responds to "/time"  
async def handle_command(payload, slack = Depends(init_slack)):
    channel = payload["channel_id"]
    user_id = payload["user_id"]

    slack.client.chat_postMessage(channel=channel, user=user_id, text=payload['text'])

    return

@commands.on('error')
def log_error(exc):
    log.error(str(exc))
