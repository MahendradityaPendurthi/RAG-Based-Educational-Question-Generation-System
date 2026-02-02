import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    # API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # LLM Provider Selection (gemini or anthropic)
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")

    # Paths
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./vectordb")
    uploads_path: str = "./uploads"
    outputs_path: str = "./outputs"
    logs_path: str = "./logs"

    # Vector DB
    collection_name: str = os.getenv("COLLECTION_NAME", "educational_content")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # LLM Settings
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))

    # Chunking
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # API Server
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "./logs/app.log")

# Create settings instance
settings = Settings()

# Ensure directories exist
Path(settings.uploads_path).mkdir(parents=True, exist_ok=True)
Path(settings.outputs_path).mkdir(parents=True, exist_ok=True)
Path(settings.logs_path).mkdir(parents=True, exist_ok=True)
Path(settings.vector_db_path).mkdir(parents=True, exist_ok=True)
