"""
App settings module
"""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Simplifies work with environment
    """
    APP_VERSION: str = "na"

    CARGO_TYPES: str = "Glass;Other"

    POSTGRES_ENDPOINT: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/postgres"
    )

    BIND_HOST: str = "localhost"
    BIND_PORT: int = 8000

    DEBUG: bool = False


settings = Settings()
