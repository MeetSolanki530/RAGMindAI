from functools import lru_cache
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from app.config.settings import get_settings


@lru_cache()
def get_embedding_service() -> NVIDIAEmbeddings:
    settings = get_settings()
    return NVIDIAEmbeddings(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
    )