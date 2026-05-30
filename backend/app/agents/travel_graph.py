import re
from langgraph.graph import END, START, StateGraph

from app.agents.budget_agent import budget_agent
from app.agents.critic_agent import critic_agent
from app.agents.grounding_guard import grounding_guard_agent
from app.agents.planner_agent import planner_agent
from app.agents.retrieval_agent import retrieval_agent
from app.agents.route_agent import route_agent
from app.agents.state import TravelAgentState
from app.rag.retriever import detect_city


SUPPORTED_CITY_NAMES = [
    "Đà Lạt",
    "Đà Nẵng",
    "Hội An",
    "Hà Nội",
    "Hà Giang",
    "Hải Dương",
]

SUPPORTED_CITY_ALIASES = {
    "đà lạt": "Đà Lạt",
    "da lat": "Đà Lạt",
    "dalat": "Đà Lạt",
    "đà nẵng": "Đà Nẵng",
    "da nang": "Đà Nẵng",
    "danang": "Đà Nẵng",
    "hội an": "Hội An",
    "hoi an": "Hội An",
    "hoian": "Hội An",
    "hà nội": "Hà Nội",
    "ha noi": "Hà Nội",
    "hanoi": "Hà Nội",
    "hà giang": "Hà Giang",
    "ha giang": "Hà Giang",
    "hagiang": "Hà Giang",
    "hải dương": "Hải Dương",
    "hai duong": "Hải Dương",
    "haiduong": "Hải Dương",
}

KNOWN_UNSUPPORTED_LOCATIONS = [
    "iceland",
    "ai-xơ-len",
    "ai xơ len",
    "nhật bản",
    "japan",
    "hàn quốc",
    "korea",
    "trung quốc",
    "china",
    "thái lan",
    "thailand",
    "singapore",
    "malaysia",
    "indonesia",
    "pháp",
    "france",
    "ý",
    "italy",
    "mỹ",
    "usa",
    "united states",
    "úc",
    "australia",
    "đức",
    "germany",
    "anh",
    "uk",
    "london",
    "paris",
    "tokyo",
    "seoul",
    "bangkok",
    "bali",
    "cần thơ",
    "can tho",
    "huế",
    "hue",
    "nha trang",
    "phú quốc",
    "phu quoc",
    "sapa",
    "sa pa",
    "quảng ninh",
    "ha long",
    "hạ long",
    "ninh bình",
    "ninh binh",
]


def build_travel_graph():
    graph = StateGraph(TravelAgentState)

    graph.add_node("planner", planner_agent)
    graph.add_node("retriever", retrieval_agent)
    graph.add_node("route", route_agent)
    graph.add_node("budget", budget_agent)
    graph.add_node("grounding_guard", grounding_guard_agent)
    graph.add_node("critic", critic_agent)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "route")
    graph.add_edge("route", "budget")
    graph.add_edge("budget", "grounding_guard")
    graph.add_edge("grounding_guard", "critic")
    graph.add_edge("critic", END)

    return graph.compile()


travel_agent_graph = build_travel_graph()


def _normalize_text(text: str) -> str:
    return text.lower().strip()


def _is_travel_request(user_request: str) -> bool:
    query = _normalize_text(user_request)

    travel_keywords = [
        "đi",
        "du lịch",
        "lịch trình",
        "gợi ý",
        "tham quan",
        "khám phá",
        "tour",
        "trip",
        "travel",
        "ngày",
        "đêm",
    ]

    return any(keyword in query for keyword in travel_keywords)


def _has_supported_city(user_request: str) -> bool:
    query = _normalize_text(user_request)

    if detect_city(user_request):
        return True

    return any(alias in query for alias in SUPPORTED_CITY_ALIASES)


def _detect_unsupported_location(user_request: str) -> str | None:
    query = _normalize_text(user_request)

    for location in KNOWN_UNSUPPORTED_LOCATIONS:
        if location in query:
            return location

    patterns = [
        r"(?:đi|du lịch|tới|đến|ở|tại)\s+([A-ZÀ-Ỵa-zà-ỵ\s]{2,40})",
        r"lịch trình\s+([A-ZÀ-Ỵa-zà-ỵ\s]{2,40})",
        r"gợi ý\s+(?:lịch trình\s+)?([A-ZÀ-Ỵa-zà-ỵ\s]{2,40})",
    ]

    stop_words = [
        "một",
        "1",
        "2",
        "3",
        "4",
        "5",
        "ngày",
        "đêm",
        "với",
        "thích",
        "ngân sách",
        "lịch trình",
    ]

    for pattern in patterns:
        match = re.search(pattern, user_request, flags=re.IGNORECASE)

        if not match:
            continue

        candidate = match.group(1).strip(" .,!?;:-").lower()

        for stop_word in stop_words:
            if f" {stop_word}" in candidate:
                candidate = candidate.split(f" {stop_word}")[0].strip()

        if not candidate:
            continue

        if candidate in SUPPORTED_CITY_ALIASES:
            return None

        if len(candidate) >= 3:
            return candidate

    return None


def _build_out_of_scope_response(
    user_request: str,
    detected_location: str | None,
) -> TravelAgentState:
    supported_cities = ", ".join(SUPPORTED_CITY_NAMES)

    location_text = (
        f" về **{detected_location}**"
        if detected_location
        else ""
    )

    final_answer = f"""
Hệ thống hiện chưa có đủ dữ liệu du lịch{location_text} trong kho tri thức JSON/Qdrant, nên mình không tạo lịch trình chi tiết để tránh bịa thông tin.

Hiện Travel AI Planner chỉ hỗ trợ các điểm đến đã được chuẩn hóa trong dữ liệu nội bộ: **{supported_cities}**.

Bạn có thể thử lại với một trong các thành phố trên, ví dụ:
- Tôi muốn đi Hải Dương 1 ngày, thích di tích lịch sử và đặc sản địa phương.
- Gợi ý lịch trình Đà Nẵng 1 ngày, thích biển và ngân sách thấp.
- Tôi muốn đi Hà Giang 4 ngày, thích road trip và thiên nhiên.
""".strip()

    return {
        "user_request": user_request,
        "trip_requirements": {
            "city": detected_location or "",
            "duration_days": None,
            "duration_nights": None,
            "budget_vnd": None,
            "preferences": [],
            "travel_style": "",
            "group_type": "",
            "transport_mode": "",
            "constraints": [],
            "missing_information": [
                "Điểm đến chưa có trong dữ liệu JSON/Qdrant của hệ thống."
            ],
        },
        "retrieved_contexts": [],
        "route_plan": {
            "strategy": "Dừng workflow vì điểm đến ngoài phạm vi dữ liệu.",
            "ordered_places": [],
            "missing_coordinate_places": [],
            "route_summary": {
                "provider": "not_available",
                "profile": "not_available",
                "total_distance_km": 0,
                "total_duration_minutes": 0,
                "segments": [],
                "note": "Không tạo tuyến đường vì không có dữ liệu đáng tin cậy.",
            },
        },
        "budget_plan": {
            "user_budget_vnd": None,
            "place_budget_notes": [],
            "assessment": "Không đánh giá ngân sách vì điểm đến chưa có trong dữ liệu hệ thống.",
        },
        "grounding_guard": {
            "has_retrieved_contexts": False,
            "allowed_place_names": [],
            "route_provider": "not_available",
            "is_route_estimate_only": False,
            "warnings": [
                "Điểm đến không thuộc phạm vi dữ liệu JSON/Qdrant hiện có.",
                "Workflow đã dừng để tránh sinh lịch trình không có căn cứ.",
            ],
            "policy": {
                "only_use_retrieved_places": True,
                "no_realtime_claims": True,
                "must_disclose_missing_data": True,
                "must_disclose_route_estimate": False,
            },
        },
        "post_processing_guard": {
            "was_modified": False,
            "removed_items": [],
            "warnings": [
                "Không tạo lịch trình do không có retrieved contexts phù hợp."
            ],
            "blocked_items": [],
            "guard_applied": True,
        },
        "critique": "Workflow dừng trước Planner vì điểm đến chưa có trong dữ liệu hệ thống.",
        "final_answer": final_answer,
    }


def _should_stop_for_scope(user_request: str) -> tuple[bool, str | None]:
    if not _is_travel_request(user_request):
        return False, None

    if _has_supported_city(user_request):
        return False, None

    detected_location = _detect_unsupported_location(user_request)

    if detected_location:
        return True, detected_location

    return True, None


async def run_travel_agent(
    user_request: str,
    user_id: str = "demo_user",
    user_memories: str = "Chưa có thông tin ghi nhớ về người dùng.",
) -> TravelAgentState:
    should_stop, detected_location = _should_stop_for_scope(user_request)

    if should_stop:
        return _build_out_of_scope_response(
            user_request=user_request,
            detected_location=detected_location,
        )

    result = await travel_agent_graph.ainvoke(
        {
            "user_request": user_request,
            "user_id": user_id,
            "user_memories": user_memories,
        }
    )

    return result