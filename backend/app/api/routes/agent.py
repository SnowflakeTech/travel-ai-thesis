from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.travel_graph import run_travel_agent
from app.core.config import settings
from app.core.security import verify_demo_api_key
from app.db.session import get_db
from app.memory.extractor import extract_memories_from_message
from app.memory.service import get_user_memory_text, save_or_update_memory


router = APIRouter(dependencies=[Depends(verify_demo_api_key)])


class AgentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1200)
    user_id: str = "demo_user"


class SavedMemoryResponse(BaseModel):
    id: int
    memory_type: str
    content: str
    confidence: float


class AgentResponse(BaseModel):
    answer: str
    trip_requirements: dict[str, Any]
    retrieved_contexts: list[dict[str, Any]]
    route_plan: dict[str, Any]
    budget_plan: dict[str, Any]
    grounding_guard: dict[str, Any] = {}
    post_processing_guard: dict[str, Any] = {}
    critique: str
    saved_memories: list[SavedMemoryResponse]


@router.post("/agent/travel", response_model=AgentResponse)
async def travel_agent(
    request: AgentRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user_memory_text = await get_user_memory_text(
            db=db,
            user_id=request.user_id,
            limit=settings.MEMORY_MAX_ITEMS,
        )

        result = await run_travel_agent(
            user_request=request.message,
            user_id=request.user_id,
            user_memories=user_memory_text,
        )

        extracted = await extract_memories_from_message(request.message)

        saved_memories = []

        for memory in extracted.memories:
            saved = await save_or_update_memory(
                db=db,
                user_id=request.user_id,
                memory_type=memory.memory_type,
                content=memory.content,
                source_message=request.message,
                confidence=memory.confidence,
            )

            saved_memories.append(
                SavedMemoryResponse(
                    id=saved.id,
                    memory_type=saved.memory_type,
                    content=saved.content,
                    confidence=saved.confidence,
                )
            )

        return AgentResponse(
            answer=result.get("final_answer", ""),
            trip_requirements=result.get("trip_requirements", {}),
            retrieved_contexts=result.get("retrieved_contexts", []),
            route_plan=result.get("route_plan", {}),
            budget_plan=result.get("budget_plan", {}),
            grounding_guard=result.get("grounding_guard", {}),
            post_processing_guard=result.get("post_processing_guard", {}),
            critique=result.get("critique", ""),
            saved_memories=saved_memories,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Travel agent memory workflow error: {str(exc)}",
        )