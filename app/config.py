import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

file_path = Path(os.path.abspath(__file__)).parent.parent

class Settings(BaseSettings):
    TOKEN: str
    ADMIN: int
    MONGO_URL: str
    REDIS_URL: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def POSTGRES_URL(self):
        return f'postgresql+asyncpg://' \
                        f'{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}' \
                        f'@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'

    model_config = SettingsConfigDict(env_file=f"{file_path}/.env", env_file_encoding="utf-8")


settings = Settings()