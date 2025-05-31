# config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    IS_PROD: bool = False
    BOT_TOKEN: str
    WEBHOOK_SECRET: str

    @property
    def MODE(self):
        return "PROD" if self.IS_PROD else "DEV"

    class Config:
        env_file = ".env"

settings = Settings()
