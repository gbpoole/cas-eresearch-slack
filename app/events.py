import logging
from slackers.hooks import events

log = logging.getLogger(__name__)

@events.on("app_mention")
async def handle_mention(payload):
    log.info("App was mentioned.")
    log.debug(payload)
