from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=1200,
        description="Yêu cầu du lịch của người dùng",
    )


class ChatResponse(BaseModel):
    answer: str
    model: str
    optimized_for_free_tier: bool = True