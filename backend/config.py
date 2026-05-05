import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./chat.db")
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    
    def __init__(self):
        # Validate critical environment variables
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY must be set in environment variables")
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in environment variables. Generate one with: openssl rand -hex 32")
    
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Gemini Chatbot")
    SMTP_MOCK_MODE: bool = os.getenv("SMTP_MOCK_MODE", "false").lower() == "true"
    
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    MAX_HISTORY_LIMIT: int = int(os.getenv("MAX_HISTORY_LIMIT", "5"))
    NOTIFICATION_POLL_INTERVAL: int = int(os.getenv("NOTIFICATION_POLL_INTERVAL", "10"))
    
    RATE_LIMIT_MAX_RETRIES: int = int(os.getenv("RATE_LIMIT_MAX_RETRIES", "3"))
    RATE_LIMIT_BACKOFF_BASE: int = int(os.getenv("RATE_LIMIT_BACKOFF_BASE", "5"))


settings = Settings()
