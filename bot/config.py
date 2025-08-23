from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram Bot
    telegram_bot_token: str

    # MrStone API
    mrstone_api_url: str
    mrstone_api_auth_token: str

    class Config:
        env_file = Path(__file__).parent / '.env'


settings = Settings()
