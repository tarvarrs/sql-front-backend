import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DB_URL")
    GAME_DATABASE_URL: str = os.getenv("GAME_DATABASE_URL")
    SECRET_KEY: str = os.getenv("ACCESS_TOKEN_SECRET")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TASK_POINTS: list = [100, 300, 500]
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD")

    class Config:
        env_file = ".env"

settings = Settings()
