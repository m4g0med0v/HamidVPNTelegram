from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: Optional[str] = None
    DB_HOST: str
    DB_PORT: Optional[str] = None
    DB_NAME: str

    # DATABASE_SQLITE = 'sqlite+aiosqlite:///data/db.sqlite3'
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def DB_URL(self):
        url = f"postgresql+asyncpg://{self.DB_USER}"
        if self.DB_PASSWORD:
            url += f":{self.DB_PASSWORD}"
        url += f"@{self.DB_HOST}"
        if self.DB_HOST != "localhost" and self.DB_PORT:
            url += f":{self.DB_PORT}"
        url += f"/{self.DB_NAME}"

        return url


class AezaSettings(BaseSettings):
    AEZA_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings:
    db = DBSettings()
    aeza = AezaSettings()


settings = Settings()
