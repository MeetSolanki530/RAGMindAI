from functools import lru_cache
from langchain_community.vectorstores import FAISS
from app.config.settings import get_settings
from app.rag.embeddings import get_embedding_service


@lru_cache()
def load_faiss_index():
    settings = get_settings()
    vectorstore = FAISS.load_local(
        folder_path=settings.vector_store_path,
        embeddings=get_embedding_service(),
        allow_dangerous_deserialization=True,
    )
    return vectorstore.as_retriever(
        search_kwargs={"k": settings.max_context_chunks},
    )