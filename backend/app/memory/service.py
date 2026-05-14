import re

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_memory import UserMemory


def normalize_memory_content(content: str) -> str:
    text = content.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace(".", "")
    text = text.replace(",", "")
    return text[:500]


async def save_or_update_memory(
    db: AsyncSession,
    user_id: str,
    memory_type: str,
    content: str,
    source_message: str | None = None,
    confidence: float = 0.8,
) -> UserMemory:
    normalized_content = normalize_memory_content(content)

    result = await db.execute(
        select(UserMemory).where(
            UserMemory.user_id == user_id,
            UserMemory.memory_type == memory_type,
            UserMemory.normalized_content == normalized_content,
        )
    )

    existing = result.scalar_one_or_none()

    if existing:
        existing.source_message = source_message or existing.source_message
        existing.confidence = max(existing.confidence or 0.0, confidence)
        existing.is_active = True

        await db.commit()
        await db.refresh(existing)

        return existing

    memory = UserMemory(
        user_id=user_id,
        memory_type=memory_type,
        content=content,
        normalized_content=normalized_content,
        source_message=source_message,
        confidence=confidence,
        is_active=True,
    )

    db.add(memory)
    await db.commit()
    await db.refresh(memory)

    return memory


async def get_user_memories(
    db: AsyncSession,
    user_id: str,
    limit: int = 20,
) -> list[UserMemory]:
    result = await db.execute(
        select(UserMemory)
        .where(
            UserMemory.user_id == user_id,
            UserMemory.is_active.is_(True),
        )
        .order_by(UserMemory.updated_at.desc())
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_user_memory_text(
    db: AsyncSession,
    user_id: str,
    limit: int = 20,
) -> str:
    memories = await get_user_memories(
        db=db,
        user_id=user_id,
        limit=limit,
    )

    if not memories:
        return "Chưa có thông tin ghi nhớ về người dùng."

    lines = []

    for memory in memories:
        lines.append(f"- {memory.memory_type}: {memory.content}")

    return "\n".join(lines)


async def deactivate_memory(
    db: AsyncSession,
    user_id: str,
    memory_id: int,
) -> bool:
    result = await db.execute(
        update(UserMemory)
        .where(
            UserMemory.id == memory_id,
            UserMemory.user_id == user_id,
        )
        .values(is_active=False)
    )

    await db.commit()

    return result.rowcount > 0