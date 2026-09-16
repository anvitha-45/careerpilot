import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "CareerPilot AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # Security
    JWT_SECRET: str = "careerpilot-super-secret-jwt-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    MONGODB_URI: str = ""
    MONGODB_DB_NAME: str = "careerpilot_db"

    # AI Providers
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    AI_PROVIDER: str = "auto"  # "gemini" | "groq" | "auto"

    # Automation
    PLAYWRIGHT_HEADLESS: bool = False
    PLAYWRIGHT_TIMEOUT: int = 30000

    # External APIs
    GITHUB_TOKEN: str = ""

    # Paths
    UPLOAD_DIR: str = os.path.join(os.path.dirname(__file__), "..", "uploads")
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "..", "server", "data")

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)

