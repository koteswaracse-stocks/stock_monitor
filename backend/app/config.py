import os
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Stock Monitor AI"
    environment: str = "development"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/stock_monitor",
    )
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", str(BASE_DIR / "app" / "data" / "faiss_index"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    broker_mode: str = os.getenv("BROKER_MODE", "demo")
    robinhood_access_token: str = os.getenv("ROBINHOOD_ACCESS_TOKEN", "")
    robinhood_base_url: str = os.getenv("ROBINHOOD_BASE_URL", "https://api.robinhood.com")

    class Config:
        env_file = BASE_DIR / ".env"
        extra = "ignore"


settings = Settings()
