import json
import re

from google.genai import types

from app.agents.state import TravelAgentState
from app.ai.gemini_client import client
from app.core.config import settings


def _extract_json_object(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)

    if not match:
        return {}

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


async def planner_agent(state: TravelAgentState) -> TravelAgentState:
    user_request = state["user_request"]

    prompt = f"""
Bạn là Planner Agent trong hệ thống AI lập kế hoạch du lịch.

Nhiệm vụ:
Phân tích yêu cầu người dùng và trích xuất thông tin thành JSON hợp lệ.

Yêu cầu người dùng:
{user_request}

Chỉ trả về JSON, không markdown, không giải thích.

Schema:
{{
  "city": "",
  "duration_days": null,
  "duration_nights": null,
  "budget_vnd": null,
  "preferences": [],
  "travel_style": "",
  "group_type": "",
  "transport_mode": "walking",
  "constraints": [],
  "missing_information": []
}}
""".strip()

    response = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=350,
            thinking_config=types.ThinkingConfig(
                thinking_budget=settings.GEMINI_THINKING_BUDGET
            ),
        ),
    )

    raw_text = response.text or ""
    requirements = _extract_json_object(raw_text)

    if not requirements:
        requirements = {
            "city": "",
            "duration_days": None,
            "duration_nights": None,
            "budget_vnd": None,
            "preferences": [],
            "travel_style": "",
            "group_type": "",
            "transport_mode": "walking",
            "constraints": [],
            "missing_information": ["Không parse được JSON từ Planner Agent"],
            "raw_output": raw_text,
        }

    return {
        "trip_requirements": requirements,
    }