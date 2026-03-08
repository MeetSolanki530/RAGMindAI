from functools import lru_cache
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from app.config.settings import get_settings


@lru_cache()
def get_llm() -> ChatNVIDIA:
    settings = get_settings()
    return ChatNVIDIA(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.model_name,
    )