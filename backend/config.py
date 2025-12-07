from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI (embeddings only, optional)
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_chat_model: str = Field("gpt-4.1-mini", env="OPENAI_CHAT_MODEL")
    openai_embedding_model: str = Field("text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL")

    # OpenRouter (primary chat LLM)
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field("meta-llama/llama-3.1-8b-instruct:free", env="OPENROUTER_MODEL")

    class Config:
        # Resolve .env relative to this file so uvicorn CWD doesn't matter
        env_file = str(Path(__file__).resolve().parent / ".env")
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
