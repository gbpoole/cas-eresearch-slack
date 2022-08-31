from fastapi import Depends
from slackers.server import commands
from logging import getLogger
import app.slack
import app.coda
import app.config

log = getLogger(__name__)

@commands.on("time")  # responds to "/time"  
async def handle_command(payload, slack = app.slack.get_client(app.config.get_settings()), coda = app.coda.get_client(app.config.get_settings())):

    slack.message(payload,"Not Ephermeral: "+payload["text"], ephemeral=False)
    slack.message(payload,"Ephermeral: "+payload["text"])

    return

@commands.on('error')
def log_error(exc):
    log.error(str(exc))
