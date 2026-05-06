from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database
    database_url: str = (
        "postgresql+asyncpg://vectorcms:vectorcms@localhost:5432/vectorcms"
    )
    database_url_sync: str = (
        "postgresql+psycopg2://vectorcms:vectorcms@localhost:5432/vectorcms"
    )

    # Embedding
    embedding_provider: str = "local"  # "local" | "deepseek"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimensions: int = 384

    # DeepSeek API
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_chat_model: str = "deepseek-chat"
    deepseek_embedding_model: str = ""

    # LLM chat defaults
    llm_provider: str = "deepseek"
    chat_model: str = "deepseek-chat"
    chat_max_tokens: int = 2048
    chat_temperature: float = 0.7

    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Search defaults
    search_default_top_k: int = 5
    hybrid_vector_weight: float = 0.7
    hybrid_keyword_weight: float = 0.3


@lru_cache
def get_settings() -> Settings:
    return Settings()
