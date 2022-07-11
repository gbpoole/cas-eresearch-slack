import logging
from slackers.hooks import commands

log = logging.getLogger(__name__)

@commands.on('error')
def log_error(exc):
    log.error(str(exc))
