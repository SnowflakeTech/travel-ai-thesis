from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.rag.retriever import retrieve_context
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_chat_answer, stream_chat_answer


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer = await generate_chat_answer(request.message, use_rag=True)

        return ChatResponse(
            answer=answer,
            model=settings.GEMINI_MODEL,
            optimized_for_free_tier=True,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG chat error: {str(exc)}",
        )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(
        stream_chat_answer(request.message, use_rag=True),
        media_type="text/plain",
    )


@router.post("/rag/search")
async def rag_search(request: ChatRequest):
    results = retrieve_context(request.message, limit=settings.RAG_TOP_K)

    return {
        "query": request.message,
        "collection": settings.QDRANT_COLLECTION,
        "top_k": settings.RAG_TOP_K,
        "results": results,
    }