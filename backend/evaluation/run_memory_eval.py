import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.agents.travel_graph import run_travel_agent


RESULT_PATH = Path("evaluation/results/memory_eval_results.json")


async def main():
    user_id = "eval_memory_user"

    memory_text = """
- travel_preference: Người dùng thích cafe chill.
- mobility_constraint: Người dùng không thích đi bộ nhiều.
- budget_preference: Người dùng ưu tiên lịch trình tiết kiệm.
""".strip()

    question = "Gợi ý lịch trình Đà Lạt 2 ngày 1 đêm."

    no_memory_result = await run_travel_agent(
        user_request=question,
        user_id=user_id,
        user_memories="Chưa có thông tin ghi nhớ về người dùng.",
    )

    with_memory_result = await run_travel_agent(
        user_request=question,
        user_id=user_id,
        user_memories=memory_text,
    )

    result = {
        "question": question,
        "memory_text": memory_text,
        "no_memory_answer": no_memory_result.get("final_answer", ""),
        "with_memory_answer": with_memory_result.get("final_answer", ""),
        "expected_personalization": [
            "Ưu tiên cafe chill",
            "Hạn chế đi bộ nhiều",
            "Ưu tiên ngân sách tiết kiệm"
        ],
    }

    RESULT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Memory evaluation saved to:", RESULT_PATH)


if __name__ == "__main__":
    asyncio.run(main())