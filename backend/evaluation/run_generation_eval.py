import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from google.genai import types

from app.agents.travel_graph import run_travel_agent
from app.ai.gemini_client import client
from app.ai.prompts import TRAVEL_RAG_SYSTEM_PROMPT
from app.core.config import settings
from app.rag.retriever import format_contexts, retrieve_context


DATASET_PATH = Path("evaluation/datasets/generation_eval_questions.json")
RESULT_PATH = Path("evaluation/results/generation_results.json")


def load_existing_results() -> dict:
    if not RESULT_PATH.exists():
        return {}

    data = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    return {
        f"{item['id']}::{item['method']}": item
        for item in data
    }


def save_results(results: list[dict]) -> None:
    RESULT_PATH.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


async def generate_basic_rag_answer(question: str) -> dict:
    contexts = retrieve_context(question, limit=7)
    context_text = format_contexts(contexts)

    prompt = f"""
{TRAVEL_RAG_SYSTEM_PROMPT}

NGỮ CẢNH DU LỊCH:
{context_text}

YÊU CẦU NGƯỜI DÙNG:
{question}

Trả lời ngắn gọn, có cấu trúc, không bịa dữ liệu ngoài ngữ cảnh.
""".strip()

    response = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=900,
            thinking_config=types.ThinkingConfig(
                thinking_budget=settings.GEMINI_THINKING_BUDGET
            ),
        ),
    )

    return {
        "answer": response.text or "",
        "retrieved_contexts": contexts,
    }


async def generate_agentic_rag_answer(question: str) -> dict:
    result = await run_travel_agent(
        user_request=question,
        user_id="eval_user",
        user_memories="Chưa có thông tin ghi nhớ về người dùng.",
    )

    return {
        "answer": result.get("final_answer", ""),
        "retrieved_contexts": result.get("retrieved_contexts", []),
        "route_plan": result.get("route_plan", {}),
        "budget_plan": result.get("budget_plan", {}),
        "grounding_guard": result.get("grounding_guard", {}),
    }


async def main():
    questions = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    existing_map = load_existing_results()
    results = list(existing_map.values())

    for item in questions:
        question_id = item["id"]
        question = item["question"]

        for method in ["basic_rag", "agentic_rag"]:
            key = f"{question_id}::{method}"

            if key in existing_map:
                print(f"Skip cached result: {key}")
                continue

            print("=" * 80)
            print("Running:", key)
            print(question)

            if method == "basic_rag":
                output = await generate_basic_rag_answer(question)
            else:
                output = await generate_agentic_rag_answer(question)

            result = {
                "id": question_id,
                "method": method,
                "question": question,
                "city": item.get("city"),
                "evaluation_focus": item.get("evaluation_focus", []),
                **output,
            }

            results.append(result)
            save_results(results)

            print("Saved:", key)

    print("Generation evaluation completed.")
    print("Results saved to:", RESULT_PATH)


if __name__ == "__main__":
    asyncio.run(main())