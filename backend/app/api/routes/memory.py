from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.memory.service import deactivate_memory, get_user_memories


router = APIRouter()


@router.get("/memory/{user_id}")
async def list_user_memories(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    memories = await get_user_memories(db=db, user_id=user_id)

    return [
        {
            "id": memory.id,
            "user_id": memory.user_id,
            "memory_type": memory.memory_type,
            "content": memory.content,
            "confidence": memory.confidence,
            "source_message": memory.source_message,
            "created_at": memory.created_at,
            "updated_at": memory.updated_at,
            "last_used_at": memory.last_used_at,
        }
        for memory in memories
    ]


@router.delete("/memory/{user_id}/{memory_id}")
async def delete_user_memory(
    user_id: str,
    memory_id: int,
    db: AsyncSession = Depends(get_db),
):
    deleted = await deactivate_memory(
        db=db,
        user_id=user_id,
        memory_id=memory_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")

    return {
        "status": "ok",
        "message": "Memory deactivated successfully",
    }