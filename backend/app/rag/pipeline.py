import json
from typing import AsyncGenerator

from app.rag.retriever import load_faiss_index
from app.config.prompts import SYSTEM_PROMPT_TEMPLATE
from app.services.llm_service import get_llm


class RAGPipeline:

    def __init__(self):
        self.retriever = load_faiss_index()
        self.llm = get_llm()

    def _retrieve(self, question: str) -> list:
        return self.retriever.invoke(question)

    def _build_prompt(self, context: str, question: str) -> str:
        return SYSTEM_PROMPT_TEMPLATE.format(context=context, question=question)

    async def stream_answer(self, question: str, history: list) -> AsyncGenerator[str, None]:
        """Stream LLM tokens as SSE events, then emit context as a final event."""
        docs = self._retrieve(question)
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = self._build_prompt(context, question)

        # Stream each token
        async for chunk in self.llm.astream(prompt):
            token = chunk.content
            if token:
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        # After stream is complete, send the retrieved context
        context_payload = [
            {"content": doc.page_content, "metadata": doc.metadata}
            for doc in docs
        ]
        yield f"data: {json.dumps({'type': 'context', 'content': context_payload})}\n\n"
        yield "data: [DONE]\n\n"

    async def generate_answer(self, question: str, history: list) -> dict:
        """Non-streaming fallback."""
        docs = self._retrieve(question)
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = self._build_prompt(context, question)
        response = await self.llm.ainvoke(prompt)
        return {
            "answer": response.content,
            "context": [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in docs
            ],
        }
