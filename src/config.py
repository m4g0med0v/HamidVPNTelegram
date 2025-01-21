from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class TgSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        extra="ignore",
    )

    bot_token: str


class DataBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        extra="ignore",
    )

    db_dialect: str
    db_driver: str
    db_user: str
    db_password: Optional[str | None] = None
    db_host: str
    db_port: Optional[str | None] = None
    db_name: str

    @property
    def db_url(self) -> str:
        link = f"{self.db_dialect}+{self.db_driver}://{self.db_user}"
        if self.db_password:
            link += f":{self.db_password}"
        if self.db_port:
            link += f"@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            link += f"@{self.db_host}/{self.db_name}"

        return link


tg_settings = TgSettings()
db_settings = DataBaseSettings()
