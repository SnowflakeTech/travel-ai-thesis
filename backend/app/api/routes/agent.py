from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from google.genai import types
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.travel_graph import run_travel_agent
from app.ai.gemini_client import client
from app.core.config import settings
from app.core.security import verify_demo_api_key
from app.db.session import get_db
from app.memory.extractor import extract_memories_from_message
from app.memory.service import get_user_memory_text, save_or_update_memory
from app.rag.retriever import format_contexts, retrieve_context


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


class ComparePromptsRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1200)
    user_id: str = "demo_user"


class ComparePromptsResponse(BaseModel):
    llm_only: str
    rag_only: str
    rag_agentic: str
    differences: str
    rag_contexts: list[dict[str, Any]] = Field(default_factory=list)


async def _generate_gemini_text(
    prompt: str,
    max_output_tokens: int | None = None,
) -> str:
    response = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=max_output_tokens or settings.GEMINI_MAX_OUTPUT_TOKENS,
            thinking_config=types.ThinkingConfig(
                thinking_budget=settings.GEMINI_THINKING_BUDGET
            ),
        ),
    )

    return response.text or ""


async def _compact_agentic_answer(
    user_request: str,
    answer: str,
) -> str:
    if not answer.strip():
        return ""

    prompt = f"""
Bạn là bộ biên tập kết quả so sánh hệ thống AI du lịch.

Nhiệm vụ:
Viết lại câu trả lời Agentic RAG bên dưới cho gọn, rõ và phù hợp để đặt trong tab so sánh.

Yêu cầu người dùng:
{user_request}

Câu trả lời Agentic RAG gốc:
{answer}

Yêu cầu trình bày:
## Kết quả từ Agentic RAG

### Tóm tắt
Viết 1 câu ngắn.

### Lịch trình / gợi ý chính
- Tối đa 4 gạch đầu dòng.
- Mỗi gạch đầu dòng tối đa 1 câu.
- Chỉ giữ ý quan trọng.

### Điểm kiểm soát
- Nêu ngắn hệ thống có dùng workflow agent, dữ liệu truy xuất, route/budget/guard nếu có.

Quy tắc:
- Không thêm địa điểm mới.
- Không thêm giá vé, giờ mở cửa hoặc dữ liệu thời gian thực.
- Không viết quá 220 từ.
- Không dùng bảng.
""".strip()

    return await _generate_gemini_text(prompt, max_output_tokens=500)


def _build_compare_summary(
    contexts: list[dict[str, Any]],
    agentic_result: dict[str, Any],
) -> str:
    context_titles = [
        str(item.get("title"))
        for item in contexts
        if item.get("title")
    ]

    context_summary = (
        ", ".join(context_titles[:6])
        if context_titles
        else "Không có retrieved contexts phù hợp."
    )

    route_provider = (
        agentic_result.get("route_plan", {})
        .get("route_summary", {})
        .get("provider", "không xác định")
    )

    grounding_warnings = agentic_result.get("grounding_guard", {}).get(
        "warnings", []
    )
    post_warnings = agentic_result.get("post_processing_guard", {}).get(
        "warnings", []
    )

    warning_lines = grounding_warnings + post_warnings

    differences = [
        "## Nhận xét khác biệt",
        "",
        "- **LLM thuần** trả lời trực tiếp từ Gemini, không dùng dữ liệu JSON hoặc Qdrant nên có nguy cơ đưa thêm thông tin ngoài kho tri thức.",
        f"- **Basic RAG** dùng dữ liệu truy xuất từ Qdrant. Một số context chính gồm: {context_summary}. Cách này bám dữ liệu hơn LLM thuần nhưng chưa có workflow kiểm tra tuyến đường, ngân sách và hậu kiểm.",
        f"- **Agentic RAG** dùng workflow Planner → Retriever → Route → Budget → Grounding Guard → Critic. Route provider hiện tại: `{route_provider}`. Vì vậy phản hồi có cấu trúc rõ hơn và kiểm soát hallucination tốt hơn.",
    ]

    if warning_lines:
        differences.extend(
            [
                "",
                "### Cảnh báo từ guard",
                *[f"- {item}" for item in warning_lines[:4]],
            ]
        )

    return "\n".join(differences)


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


@router.post("/agent/compare-prompts", response_model=ComparePromptsResponse)
async def compare_prompts(
    request: ComparePromptsRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user_memory_text = await get_user_memory_text(
            db=db,
            user_id=request.user_id,
            limit=settings.MEMORY_MAX_ITEMS,
        )

        llm_prompt = f"""
Bạn là trợ lý du lịch.

Yêu cầu người dùng:
{request.message}

Hãy trả lời bằng tiếng Việt theo cấu trúc sau:

## Gợi ý từ LLM thuần

### Tóm tắt nhu cầu
Viết 1 câu ngắn tóm tắt nhu cầu người dùng.

### Lịch trình đề xuất
- Tối đa 4 gạch đầu dòng.
- Mỗi gạch đầu dòng tối đa 1 câu.
- Không viết quá chi tiết.

### Ngân sách tham khảo
- Chỉ nêu ở mức chung nếu không có dữ liệu cụ thể.

### Lưu ý
- Nêu tối đa 2 lưu ý thực tế.

Quy tắc:
- Không viết quá 220 từ.
- Không dùng bảng.
- Không viết lời chào dài.
- Không khẳng định giá vé, giờ mở cửa hoặc tình trạng hiện tại nếu không chắc chắn.
""".strip()

        llm_only = await _generate_gemini_text(
            llm_prompt,
            max_output_tokens=500,
        )

        contexts = retrieve_context(
            query=request.message,
            limit=max(settings.RAG_TOP_K, 7),
            use_filter=True,
        )

        formatted_contexts = format_contexts(contexts)

        rag_prompt = f"""
Bạn là trợ lý du lịch sử dụng dữ liệu truy xuất từ hệ thống.

QUY TẮC BẮT BUỘC:
- Chỉ sử dụng địa điểm có trong ngữ cảnh truy xuất.
- Không tự thêm địa điểm mới.
- Không bịa giá vé, giờ mở cửa, tình trạng đông khách hoặc dữ liệu thời gian thực.
- Nếu dữ liệu chưa đủ, hãy nói rõ: "Hệ thống hiện chưa có đủ dữ liệu để khẳng định chi tiết này."

Yêu cầu người dùng:
{request.message}

Ngữ cảnh truy xuất:
{formatted_contexts}

Hãy trả lời bằng tiếng Việt theo cấu trúc sau:

## Gợi ý từ Basic RAG

### Dữ liệu được sử dụng
Nêu 1 câu ngắn về các địa điểm chính được lấy từ ngữ cảnh.

### Lịch trình đề xuất
- Tối đa 4 gạch đầu dòng.
- Mỗi gạch đầu dòng tối đa 1 câu.
- Chỉ dùng địa điểm trong ngữ cảnh.

### Ngân sách tham khảo
- Chỉ nêu theo dữ liệu có trong ngữ cảnh.

### Lưu ý về dữ liệu
- Nêu ngắn nếu dữ liệu còn thiếu.

Quy tắc:
- Không viết quá 220 từ.
- Không dùng bảng.
- Không thêm địa điểm ngoài retrieved contexts.
""".strip()

        rag_only = await _generate_gemini_text(
            rag_prompt,
            max_output_tokens=500,
        )

        agentic_result = await run_travel_agent(
            user_request=request.message,
            user_id=request.user_id,
            user_memories=user_memory_text,
        )

        raw_agentic_answer = agentic_result.get("final_answer", "")
        compact_agentic_answer = await _compact_agentic_answer(
            user_request=request.message,
            answer=raw_agentic_answer,
        )

        differences = _build_compare_summary(
            contexts=contexts,
            agentic_result=agentic_result,
        )

        return ComparePromptsResponse(
            llm_only=llm_only,
            rag_only=rag_only,
            rag_agentic=compact_agentic_answer or raw_agentic_answer,
            differences=differences,
            rag_contexts=contexts,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Compare prompts workflow error: {str(exc)}",
        )