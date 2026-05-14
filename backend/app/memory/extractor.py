import json
import re

from google.genai import types

from app.ai.gemini_client import client
from app.core.config import settings
from app.memory.schemas import MemoryExtractionResult


MEMORY_KEYWORDS = [
    "tôi thích",
    "mình thích",
    "tui thích",
    "em thích",
    "không thích",
    "không muốn",
    "ghét",
    "ưu tiên",
    "thường đi",
    "hay đi",
    "ngân sách thấp",
    "tiết kiệm",
    "cao cấp",
    "sang trọng",
    "ít đi bộ",
    "không đi bộ nhiều",
    "thích cafe",
    "thích cà phê",
    "thích biển",
    "thích núi",
    "thích thiên nhiên",
    "thích road trip",
    "đi cùng gia đình",
    "đi cùng người yêu",
    "đi cùng bạn bè",
]


def should_extract_memory(message: str) -> bool:
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in MEMORY_KEYWORDS)


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)

    if not match:
        return {"memories": []}

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"memories": []}


async def extract_memories_from_message(message: str) -> MemoryExtractionResult:
    if not settings.MEMORY_ENABLE_LLM_EXTRACTION:
        return MemoryExtractionResult(memories=[])

    if not should_extract_memory(message):
        return MemoryExtractionResult(memories=[])

    prompt = f"""
Bạn là Memory Extractor cho hệ thống AI du lịch.

Nhiệm vụ:
Trích xuất các thông tin bền vững có thể dùng để cá nhân hóa tư vấn du lịch trong tương lai.

Chỉ lưu:
- sở thích du lịch
- phong cách du lịch
- ngân sách thường ưu tiên
- hạn chế khi di chuyển
- loại địa điểm yêu thích
- loại địa điểm không thích
- thói quen ăn uống
- nhóm người thường đi cùng

Không lưu:
- điểm đến của riêng chuyến hiện tại
- số ngày của riêng chuyến hiện tại
- ngày tháng cụ thể
- ngân sách nếu chỉ nói cho một chuyến cụ thể
- thông tin quá nhạy cảm hoặc không liên quan du lịch

Tin nhắn người dùng:
{message}

Chỉ trả về JSON hợp lệ theo schema:
{{
  "memories": [
    {{
      "memory_type": "travel_preference",
      "content": "Người dùng thích cafe chill.",
      "confidence": 0.9
    }}
  ]
}}

Các memory_type hợp lệ:
- travel_preference
- travel_dislike
- budget_preference
- mobility_constraint
- travel_style
- food_preference
- companion_preference

Nếu không có gì đáng nhớ, trả về:
{{"memories": []}}
""".strip()

    try:
        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=settings.MEMORY_EXTRACTION_MAX_OUTPUT_TOKENS,
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(
                    thinking_budget=settings.GEMINI_THINKING_BUDGET
                ),
            ),
        )

        raw_text = response.text or ""
        data = _extract_json(raw_text)

        return MemoryExtractionResult(**data)

    except Exception:
        return MemoryExtractionResult(memories=[])