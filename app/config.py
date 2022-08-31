import logging
import os
from functools import lru_cache
from pydantic import BaseSettings, ValidationError

log = logging.getLogger(__name__)


class Settings(object):

    log.info("Loading config settings from the environment...")

    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = os.getenv("TESTING", 0)

    if environment=="dev":
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    CODA_API_TOKEN: str = os.environ['CODA_TOKEN']
    CODA_DOC_ID: str = "3zs35nY4oB"
    CODA_HEADERS: dict = {'Authorization': f"Bearer {CODA_API_TOKEN}"}
    SLACK_BOT_TOKEN: str = os.environ['SLACK_BOT_TOKEN']

@lru_cache()
def get_settings() -> Settings:
    return Settings()
