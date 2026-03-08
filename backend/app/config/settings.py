import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Project root: config/ -> app/ -> backend/ -> project root
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")


class Settings(BaseModel):
    # API / LLM
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "")
    model_name: str = os.getenv("MODEL_NAME", "")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "")

    # Vector store
    vector_db: str = os.getenv("VECTOR_DB", "faiss")
    vector_store_path: str = str(PROJECT_ROOT / os.getenv("VECTOR_STORE_PATH", "vector_store"))

    # Chunking
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    max_context_chunks: int = int(os.getenv("MAX_CONTEXT_CHUNKS", "5"))

    # Documents
    document_folder: str = str(PROJECT_ROOT / os.getenv("DOCUMENT_FOLDER", "data/documents"))


@lru_cache()
def get_settings() -> Settings:
    return Settings()