"""Configuration settings for the application."""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings."""

    def __init__(self):
        """Initialize settings with environment variables."""
        # Redis Configuration
        self.REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

        # Celery Configuration
        broker_url = os.getenv("CELERY_BROKER_URL", None)
        result_backend = os.getenv("CELERY_RESULT_BACKEND", None)
        
        if broker_url is None:
            broker_url = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        if result_backend is None:
            result_backend = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        
        self.CELERY_BROKER_URL: str = broker_url
        self.CELERY_RESULT_BACKEND: str = result_backend

        # API Configuration
        self.API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT: int = int(os.getenv("API_PORT", "8000"))

        # Engine Paths
        self.STOCKFISH_PATH: str = os.getenv("STOCKFISH_PATH", "stockfish")
        self.LCZERO_PATH: str = os.getenv("LCZERO_PATH", "")

        # Metrics
        self.METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))


settings = Settings()

