from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    memory_type: str = Field(..., description="Loại memory")
    content: str = Field(..., description="Nội dung memory")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class MemoryExtractionResult(BaseModel):
    memories: list[MemoryItem] = []