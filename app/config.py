from logging import getLogger
import os
from functools import lru_cache
from pydantic import BaseSettings, ValidationError

log = getLogger(__name__)


class Settings(BaseSettings):
    CODA_API_TOKEN: str = os.environ['CODA_TOKEN']
    CODA_DOC_ID: str = "3zs35nY4oB"
    CODA_HEADERS: dict = {'Authorization': f"Bearer {CODA_API_TOKEN}"}
    SLACK_BOT_TOKEN: str = os.environ['SLACK_BOT_TOKEN']
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = os.getenv("TESTING", 0)

@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
