from logging import getLogger
from slack_sdk import WebClient
from functools import lru_cache
from fastapi import Depends
import app.config

log = getLogger(__name__)


class SlackClient(object):

    def __init__(self, settings):

        self.client = WebClient(token=settings.SLACK_BOT_TOKEN)

    def message(self, payload, message, ephemeral=True):

        if ephemeral:
            self.client.chat_postEphemeral(channel=payload["channel_id"], user=payload["user_id"] , text= message)
        else:
            self.client.chat_postMessage(channel=payload["channel_id"], text= message)

@lru_cache
def get_client(settings: app.config.Settings) -> SlackClient:
    log.info("Initialising Slack client...")
    return SlackClient(settings)
