from app.agents.state import TravelAgentState


REAL_TIME_RISK_KEYWORDS = [
    "giá vé hiện tại",
    "giá chính xác",
    "giờ mở cửa hiện tại",
    "đang mở cửa",
    "đang đóng cửa",
    "đông khách hiện tại",
    "tình trạng đông",
    "thời tiết hiện tại",
    "kẹt xe",
    "còn phòng",
    "vé máy bay",
    "giá khách sạn hiện tại",
]


def _get_allowed_place_names(contexts: list[dict]) -> list[str]:
    names = []

    for item in contexts:
        title = item.get("title")

        if title and title not in names:
            names.append(title)

    return names


def _get_route_provider(route_plan: dict) -> str:
    route_summary = route_plan.get("route_summary") or {}
    provider = route_summary.get("provider")

    if not provider:
        return "unknown"

    return str(provider)


def _is_haversine_route(route_plan: dict) -> bool:
    provider = _get_route_provider(route_plan)
    return provider == "haversine_fallback"


def grounding_guard_agent(state: TravelAgentState) -> TravelAgentState:
    contexts = state.get("retrieved_contexts", [])
    route_plan = state.get("route_plan", {})

    allowed_place_names = _get_allowed_place_names(contexts)
    route_provider = _get_route_provider(route_plan)
    is_haversine = _is_haversine_route(route_plan)

    has_retrieved_contexts = len(contexts) > 0
    has_allowed_places = len(allowed_place_names) > 0

    warnings = []

    if not has_retrieved_contexts:
        warnings.append(
            "Không tìm thấy dữ liệu phù hợp trong RAG. Câu trả lời cần nói rõ hệ thống chưa có đủ dữ liệu."
        )

    if is_haversine:
        warnings.append(
            "Tuyến đường đang dùng Haversine fallback. Khoảng cách chỉ là ước lượng theo đường thẳng, không phải tuyến đường thực tế."
        )

    guard = {
        "has_retrieved_contexts": has_retrieved_contexts,
        "allowed_place_names": allowed_place_names,
        "route_provider": route_provider,
        "is_route_estimate_only": is_haversine,
        "real_time_risk_keywords": REAL_TIME_RISK_KEYWORDS,
        "warnings": warnings,
        "policy": {
            "only_use_retrieved_places": True,
            "no_realtime_claims": True,
            "must_disclose_missing_data": True,
            "must_disclose_route_estimate": is_haversine,
        },
    }

    return {
        "grounding_guard": guard,
    }