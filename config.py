"""
Configuration management for SolvIQ RAG system
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")
    
    # Application settings
    app_name: str = "SolvIQ"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    frontend_port: int = Field(default=8501, env="FRONTEND_PORT")
    
    # Data settings
    data_path: str = Field(default="data", env="DATA_PATH")
    
    # RAG settings
    chunk_size: int = Field(default=800, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, env="CHUNK_OVERLAP")
    model_name: str = Field(default="gpt-4o-mini", env="MODEL_NAME")
    temperature: float = Field(default=0.1, env="TEMPERATURE")
    max_tokens: int = Field(default=1000, env="MAX_TOKENS")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="solviq.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_data_path() -> Path:
    """Get the data directory path"""
    data_path = Path(settings.data_path)
    if not data_path.is_absolute():
        # Make relative to project root
        project_root = Path(__file__).parent
        data_path = project_root / data_path
    return data_path.resolve()


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.resolve()


def validate_settings() -> bool:
    """Validate that all required settings are present"""
    required_keys = ["openai_api_key", "tavily_api_key"]
    missing_keys = [key for key in required_keys if not getattr(settings, key)]
    
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    return True
