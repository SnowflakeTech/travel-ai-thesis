import re

from app.core.config import settings
from app.rag.cleaning import normalize_category, normalize_city
from app.rag.embedding import embed_text
from app.rag.qdrant_store import build_metadata_filter, get_qdrant_client


def shorten_text(text: str | None, max_chars: int = 450) -> str:
    if not text:
        return ""

    if len(text) <= max_chars:
        return text

    return text[:max_chars].strip() + "..."


def detect_city(query: str) -> str | None:
    query_lower = query.lower()

    city_keywords = {
        "đà lạt": "đà lạt",
        "da lat": "đà lạt",
        "dalat": "đà lạt",
        "đà nẵng": "đà nẵng",
        "da nang": "đà nẵng",
        "danang": "đà nẵng",
        "hội an": "hội an",
        "hoi an": "hội an",
        "hoian": "hội an",
        "hà nội": "hà nội",
        "ha noi": "hà nội",
        "hanoi": "hà nội",
        "hà giang": "hà giang",
        "ha giang": "hà giang",
        "hagiang": "hà giang",
        "hải dương": "hải dương",
        "hai duong": "hải dương",
        "haiduong": "hải dương",
    }

    for keyword, city in city_keywords.items():
        if keyword in query_lower:
            return normalize_city(city)

    return None


def detect_category(query: str) -> str | None:
    query_lower = query.lower()

    category_keywords = {
        "cafe": "cafe",
        "cà phê": "cafe",
        "coffee": "cafe",
        "biển": "biển",
        "beach": "biển",
        "quán ăn": "ẩm thực",
        "ăn gì": "ẩm thực",
        "đặc sản": "ẩm thực",
        "ẩm thực": "ẩm thực",
        "món địa phương": "ẩm thực",
        "món ăn địa phương": "ẩm thực",
        "tham quan": "tham quan",
        "check-in": "tham quan",
        "chụp ảnh": "tham quan",
        "thiên nhiên": "thiên nhiên",
        "nature": "thiên nhiên",
        "núi": "thiên nhiên",
        "đèo": "thiên nhiên",
        "sông": "thiên nhiên",
        "thác": "thiên nhiên",
        "hang": "thiên nhiên",
        "văn hóa": "văn hóa",
        "culture": "văn hóa",
        "lịch sử": "văn hóa",
        "bản làng": "văn hóa",
        "chợ phiên": "văn hóa",
        "phiêu lưu": "trải nghiệm",
        "khám phá": "trải nghiệm",
        "adventure": "trải nghiệm",
        "road trip": "trải nghiệm",
        "trekking": "trải nghiệm",
        "phượt": "trải nghiệm",
        "đi xe máy": "trải nghiệm",
        "lịch trình": "lịch trình",
        "hành trình": "lịch trình",
        "itinerary": "lịch trình",
    }

    for keyword, category in category_keywords.items():
        if keyword in query_lower:
            return normalize_category(category)

    return None


def is_itinerary_query(query: str) -> bool:
    query_lower = query.lower()

    itinerary_keywords = [
        "lịch trình",
        "hành trình",
        "đi",
        "du lịch",
        "road trip",
        "tour",
        "ngày",
        "đêm",
        "1 ngày",
        "2 ngày",
        "3 ngày",
        "4 ngày",
        "5 ngày",
        "6 ngày",
        "7 ngày",
    ]

    duration_pattern = r"\b\d+\s*(ngày|đêm|day|days|night|nights)\b"

    has_itinerary_keyword = any(keyword in query_lower for keyword in itinerary_keywords)
    has_duration = re.search(duration_pattern, query_lower) is not None

    return has_itinerary_keyword and has_duration


def has_multiple_travel_intents(query: str) -> bool:
    query_lower = query.lower()

    intent_groups = {
        "nature": [
            "thiên nhiên",
            "núi",
            "đèo",
            "sông",
            "hang",
            "thác",
            "cảnh đẹp",
            "ngắm cảnh",
            "cao nguyên",
        ],
        "food": [
            "ăn",
            "ẩm thực",
            "đặc sản",
            "món địa phương",
            "món ăn địa phương",
            "quán ăn",
        ],
        "culture": [
            "văn hóa",
            "bản làng",
            "chợ phiên",
            "dân tộc",
            "làng",
            "lịch sử",
        ],
        "adventure": [
            "road trip",
            "phượt",
            "trekking",
            "đi xe máy",
            "cung đường",
            "khám phá",
        ],
        "relax": [
            "nghỉ dưỡng",
            "chill",
            "nhẹ nhàng",
            "thư giãn",
        ],
    }

    matched_groups = 0

    for keywords in intent_groups.values():
        if any(keyword in query_lower for keyword in keywords):
            matched_groups += 1

    return matched_groups >= 2


def should_use_broad_city_search(query: str) -> bool:
    return is_itinerary_query(query) or has_multiple_travel_intents(query)


def boost_itinerary_contexts(contexts: list[dict]) -> list[dict]:
    priority_categories = {
        "lịch trình": 0,
        "lịch trình mẫu": 0,
        "thiên nhiên": 1,
        "trải nghiệm": 2,
        "văn hóa": 3,
        "tham quan": 3,
        "biển": 3,
        "cafe": 4,
        "ẩm thực": 5,
    }

    priority_titles = [
        "ha giang loop",
        "hà giang loop",
        "ngày 1",
        "ngày 2",
        "ngày 3",
        "ngày 4",
        "mã pí lèng",
        "ma pi leng",
        "sông nho quế",
        "nho quế",
        "lũng cú",
        "lung cu",
        "sa phin",
        "đồng văn",
        "dong van",
        "quản bạ",
        "quan ba",
    ]

    def title_priority(item: dict) -> int:
        title = str(item.get("title") or "").lower()

        for index, keyword in enumerate(priority_titles):
            if keyword in title:
                return index

        return 99

    return sorted(
        contexts,
        key=lambda item: (
            priority_categories.get(item.get("category"), 99),
            title_priority(item),
            -float(item.get("score", 0)),
        ),
    )


def diversify_contexts(
    contexts: list[dict],
    max_per_category: int = 3,
    max_total: int = 10,
) -> list[dict]:
    category_counts: dict[str, int] = {}
    diversified = []

    for item in contexts:
        category = item.get("category") or "khác"
        current_count = category_counts.get(category, 0)

        if current_count >= max_per_category:
            continue

        diversified.append(item)
        category_counts[category] = current_count + 1

        if len(diversified) >= max_total:
            break

    return diversified


def retrieve_context(
    query: str,
    limit: int | None = None,
    use_filter: bool = True,
) -> list[dict]:
    client = get_qdrant_client()
    query_vector = embed_text(query)

    is_broad_search = should_use_broad_city_search(query)

    city = detect_city(query) if use_filter else None

    if use_filter and is_broad_search:
        category = None
        search_mode = "broad_city_search"
    else:
        category = detect_category(query) if use_filter else None
        search_mode = "city_category_search"

    query_filter = build_metadata_filter(city=city, category=category)

    search_limit = limit or settings.RAG_TOP_K

    if is_broad_search:
        search_limit = max(search_limit, 18)

    result = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        query_filter=query_filter,
        limit=search_limit,
        with_payload=True,
    )

    contexts = []

    for point in result.points:
        payload = point.payload or {}

        if point.score < settings.RAG_SCORE_THRESHOLD:
            continue

        category = payload.get("category") or payload.get("category_normalized")

        contexts.append(
            {
                "score": round(point.score, 4),
                "search_mode": search_mode,
                "title": payload.get("title"),
                "city": payload.get("city"),
                "category": category,
                "address": payload.get("address"),
                "best_time": payload.get("best_time"),
                "budget": payload.get("budget"),
                "suitable_for": payload.get("suitable_for"),
                "tips": payload.get("tips"),
                "source_url": payload.get("source_url"),
                "source_file": payload.get("source_file"),
                "latitude": payload.get("latitude"),
                "longitude": payload.get("longitude"),
                "text": shorten_text(payload.get("text")),
            }
        )

    if is_broad_search:
        contexts = boost_itinerary_contexts(contexts)
        contexts = diversify_contexts(contexts, max_per_category=3, max_total=10)

    return contexts


def format_contexts(contexts: list[dict]) -> str:
    if not contexts:
        return "Không tìm thấy dữ liệu phù hợp trong kho tri thức."

    formatted = []
    current_length = 0

    for index, item in enumerate(contexts, start=1):
        block = f"""
[Ngữ cảnh {index}]
Tên: {item.get("title")}
Thành phố: {item.get("city")}
Loại hình: {item.get("category")}
Chế độ tìm kiếm: {item.get("search_mode")}
Địa chỉ: {item.get("address")}
Thời điểm phù hợp: {item.get("best_time")}
Ngân sách: {item.get("budget")}
Phù hợp với: {item.get("suitable_for")}
Lưu ý: {item.get("tips")}
Nguồn URL: {item.get("source_url")}
Nguồn file: {item.get("source_file")}
Nội dung: {item.get("text")}
Độ liên quan: {item.get("score")}
""".strip()

        if current_length + len(block) > settings.RAG_MAX_CONTEXT_CHARS:
            break

        formatted.append(block)
        current_length += len(block)

    return "\n\n".join(formatted)