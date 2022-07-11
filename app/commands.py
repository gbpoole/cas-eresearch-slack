import logging
from slackers.hooks import commands

log = logging.getLogger(__name__)


@commands.on("time")  # responds to "/time"  
async def handle_command(payload):
    log.info("Command received")
    log.debug(payload)
