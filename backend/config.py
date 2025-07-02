from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ALLOWED_ORIGINS: List[str] = [""]
    GOOGLE_API_KEY: str
    DATABASE_URL: str
    SENDER_EMAIL: str = None
    SENDER_EMAIL_APP_PASSWORD: str = None
    SMTP_HOST: str = None
    SMTP_PORT: int = 465

    class Config:
        env_file = "backend/.env"
        extra = "ignore"

settings = Settings() 