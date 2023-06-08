from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = None
    google_application_credentials: str = None
    uvicorn_host: str = "0.0.0.0"  # noqa: S104
    uvicorn_port: int = 8080
    prompt_template_file: str = "prompt.txt"
    cors_origins: list[str] = ["*"]  # e.g. CORS_ORIGINS=["http://localhost:3000"]
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]
    cors_allow_credentials: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()
