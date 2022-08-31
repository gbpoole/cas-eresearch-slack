from logging import getLogger
from slack_sdk import WebClient
from functools import lru_cache
from fastapi import Depends
import config

log = logging.getLogger(__name__)


class SlackClient(object):

    def __init__(self,settings: config.Settings):

        client = WebClient(token=settings.SLACK_BOT_TOKEN)

def init_client(settings: config.Settings = Depends(config.get_settings)) -> object:
    log.info("Initialising Slack client...")
    return SlackClient(settings)
