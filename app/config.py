import logging
import os
import slack_sdk as slack
from functools import lru_cache
from pydantic import BaseSettings


CODA_API_TOKEN = os.environ['CODA_TOKEN']
CODA_DOC_ID = "3zs35nY4oB"
CODA_HEADERS = {'Authorization': f"Bearer {CODA_API_TOKEN}"}

class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = os.getenv("TESTING", 0)


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()

SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
web_client = slack.WebClient(token=SLACK_BOT_TOKEN)
