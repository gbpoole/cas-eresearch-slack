from fastapi import Depends, commands
from logging import getLogger
import slack
import coda
import app.config

log = getLogger(__name__)

@commands.on('error')
def log_error(exc):
    log.error(str(exc))
