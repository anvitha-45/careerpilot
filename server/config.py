import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CareerPilot"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "careerpilot")

    # LLM / AI Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "auto")  # "auto" | "gemini" | "groq" | "openai" | "heuristic"
    AI_MODEL: str = os.getenv("AI_MODEL", "")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.3"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "1200"))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_SECRET_SALT: str = os.getenv("AI_SECRET_SALT", "")

    # Playwright Browser Automation
    PLAYWRIGHT_HEADLESS: bool = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

