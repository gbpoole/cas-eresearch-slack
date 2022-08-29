import logging
import os
import slack_sdk as slack
from codaio import Coda, Document
import requests
from functools import lru_cache
from pydantic import BaseSettings, ValidationError
from fastapi import Depends

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    CODA_API_TOKEN: str = os.environ['CODA_TOKEN']
    CODA_DOC_ID: str = "3zs35nY4oB"
    CODA_HEADERS: dict = {'Authorization': f"Bearer {CODA_API_TOKEN}"}
    SLACK_BOT_TOKEN: str = os.environ['SLACK_BOT_TOKEN']
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = os.getenv("TESTING", 0)

class SlackClient(object):

    def __init__(self,settings: Settings):

        client = slack.WebClient(token=settings.SLACK_BOT_TOKEN)

class CodaClient(object):

    def __init__(self,settings: Settings):

        self.client = Coda(settings.CODA_API_TOKEN)
        self.doc    = Document(settings.CODA_DOC_ID, coda=self.client)
        self.settings = settings

    def get_rows(self, table):

        results = []
        for row in self.client.list_rows(self.doc.id, table.id, use_column_names=True)['items']:
            result = {}
            for key, value in row['values'].items():
                result[key]=value
            results.append(result)

        return results

@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()

@lru_cache()
def init_slack(settings: Settings = Depends(get_settings)) -> object:
    log.info("Initialising Slack client...")
    return SlackClient(settings)

@lru_cache()
def init_coda(settings: Settings = Depends(get_settings)) -> object:
    log.info("Initialising Coda client...")
    return CodaClient(settings)
