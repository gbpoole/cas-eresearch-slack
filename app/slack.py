from logging import getLogger
from slack_sdk import WebClient
from functools import lru_cache
from fastapi import Depends
import app.config

log = getLogger(__name__)


class SlackClient(object):

    def __init__(self, settings):

        self.client = WebClient(token=settings.SLACK_BOT_TOKEN)

@lru_cache
def get_client(settings: app.config.Settings) -> SlackClient:
    log.info("Initialising Slack client...")
    return SlackClient(settings)
