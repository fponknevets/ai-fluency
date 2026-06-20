"""Configuration management for test framework."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """Configuration loader with validation."""
    
    @staticmethod
    def _get_required(key: str) -> str:
        """Get required environment variable, raise error if missing."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Missing required environment variable: {key}")
        return value
    
    @staticmethod
    def _get_optional(key: str, default: str = None) -> str:
        """Get optional environment variable with default."""
        return os.getenv(key, default)


# Load and validate configuration on import
try:
    IDENTITY_SERVICE_URL = Config._get_required("IDENTITY_SERVICE_URL")
    TASK_SERVICE_URL = Config._get_required("TASK_SERVICE_URL")
except ValueError as e:
    raise RuntimeError(f"Configuration Error: {e}. Have you created .env from .env.example?") from e


__all__ = [
    "IDENTITY_SERVICE_URL",
    "TASK_SERVICE_URL",
]
