from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.rag.pipeline import RAGPipeline

router = APIRouter()

# Single pipeline instance reused across requests
_pipeline: RAGPipeline | None = None


def _get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


class ChatRequest(BaseModel):
    message: str
    history: list = []


@router.post("/chat")
async def chat(request: ChatRequest):
    pipeline = _get_pipeline()
    response = await pipeline.generate_answer(
        question=request.message,
        history=request.history,
    )
    return {
        "answer": response["answer"],
        "context": response["context"],
        "history": request.history,
    }


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    pipeline = _get_pipeline()
    return StreamingResponse(
        pipeline.stream_answer(question=request.message, history=request.history),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )