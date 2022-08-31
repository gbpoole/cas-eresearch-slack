from logging import getLogger
from slackers.hooks import events

log = getLogger(__name__)

@events.on("app_mention")
async def handle_mention(payload):
    log.info("App was mentioned.")
    log.debug(payload)
