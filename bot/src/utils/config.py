from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    AEZA_TOKEN: str
    DB_USER: str
    DB_PASSWORD: Optional[str] = None
    DB_HOST: str
    DB_PORT: Optional[str] = None
    DB_NAME: str

    model_config = SettingsConfigDict(env_file="../.env")

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


settings = Settings()
