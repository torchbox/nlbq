from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = None
    google_application_credentials: str = None
    uvicorn_host: str = "0.0.0.0"  # noqa: S104
    uvicorn_port: int = 8080
    prompt_template_file: str = "prompt.txt"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()
