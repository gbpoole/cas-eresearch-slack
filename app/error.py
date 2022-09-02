from logging import getLogger
from slackers.server import commands
import app.config

log = getLogger(__name__)

@commands.on('error')
def log_error(exc):
    log.error(str(exc))
