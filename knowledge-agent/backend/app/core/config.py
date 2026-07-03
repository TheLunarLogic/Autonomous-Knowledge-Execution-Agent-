"""
Application-wide settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration — reads from .env file automatically."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/knowledge_agent"

    # ── AWS Bedrock ───────────────────────────────────────────
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    BEDROCK_EMBEDDING_MODEL_ID: str = "amazon.titan-embed-text-v1"

    # ── ChromaDB ──────────────────────────────────────────────
    CHROMA_PATH: str = "./chroma_data"

    # ── App ───────────────────────────────────────────────────
    APP_NAME: str = "Knowledge Agent"
    DEBUG: bool = False


settings = Settings()
