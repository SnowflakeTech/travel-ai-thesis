from collections.abc import AsyncGenerator

from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

from app.ai.gemini_client import client
from app.ai.prompts import TRAVEL_RAG_SYSTEM_PROMPT, TRAVEL_SYSTEM_PROMPT
from app.core.config import settings
from app.rag.retriever import format_contexts, retrieve_context


def _trim_user_message(message: str) -> str:
    cleaned = message.strip()

    if len(cleaned) > settings.CHAT_MAX_INPUT_CHARS:
        cleaned = cleaned[: settings.CHAT_MAX_INPUT_CHARS]

    return cleaned


def _generation_config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        temperature=settings.GEMINI_TEMPERATURE,
        max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
        thinking_config=types.ThinkingConfig(
            thinking_budget=settings.GEMINI_THINKING_BUDGET
        ),
    )


def _build_basic_prompt(user_message: str) -> str:
    return f"""
{TRAVEL_SYSTEM_PROMPT}

YÊU CẦU NGƯỜI DÙNG:
{user_message}
""".strip()


def _build_rag_prompt(user_message: str) -> str:
    contexts = retrieve_context(user_message, limit=settings.RAG_TOP_K)
    context_text = format_contexts(contexts)

    return f"""
{TRAVEL_RAG_SYSTEM_PROMPT}

NGỮ CẢNH DU LỊCH:
{context_text}

YÊU CẦU NGƯỜI DÙNG:
{user_message}
""".strip()


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=6),
    stop=stop_after_attempt(2),
)
async def generate_chat_answer(message: str, use_rag: bool = True) -> str:
    user_message = _trim_user_message(message)

    prompt = (
        _build_rag_prompt(user_message)
        if use_rag
        else _build_basic_prompt(user_message)
    )

    response = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=_generation_config(),
    )

    if not response.text:
        return "Mình chưa tạo được câu trả lời. Bạn thử nhập yêu cầu ngắn gọn hơn nhé."

    return response.text.strip()


async def stream_chat_answer(
    message: str,
    use_rag: bool = True,
) -> AsyncGenerator[str, None]:
    user_message = _trim_user_message(message)

    prompt = (
        _build_rag_prompt(user_message)
        if use_rag
        else _build_basic_prompt(user_message)
    )

    try:
        stream = await client.aio.models.generate_content_stream(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=_generation_config(),
        )

        async for chunk in stream:
            if chunk.text:
                yield chunk.text

    except Exception as exc:
        yield f"\n[ERROR] Không gọi được Gemini API hoặc RAG pipeline: {str(exc)}"