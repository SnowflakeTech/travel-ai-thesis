from app.core.config import settings
from app.rag.cleaning import normalize_category, normalize_city
from app.rag.embedding import embed_text
from app.rag.qdrant_store import build_metadata_filter, get_qdrant_client


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
        "ăn": "ẩm thực",
        "ẩm thực": "ẩm thực",
        "quán ăn": "ẩm thực",
        "tham quan": "tham quan",
        "check-in": "tham quan",
        "chụp ảnh": "tham quan",
    }

    for keyword, category in category_keywords.items():
        if keyword in query_lower:
            return normalize_category(category)

    return None


def retrieve_context(
    query: str,
    limit: int | None = None,
    use_filter: bool = True,
) -> list[dict]:
    client = get_qdrant_client()
    query_vector = embed_text(query)

    city = detect_city(query) if use_filter else None
    category = detect_category(query) if use_filter else None
    query_filter = build_metadata_filter(city=city, category=category)

    result = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        query_filter=query_filter,
        limit=limit or settings.RAG_TOP_K,
        with_payload=True,
    )

    contexts = []

    for point in result.points:
        payload = point.payload or {}

        if point.score < settings.RAG_SCORE_THRESHOLD:
            continue

        contexts.append(
            {
                "score": round(point.score, 4),
                "title": payload.get("title"),
                "city": payload.get("city"),
                "category": payload.get("category"),
                "address": payload.get("address"),
                "best_time": payload.get("best_time"),
                "budget": payload.get("budget"),
                "suitable_for": payload.get("suitable_for"),
                "tips": payload.get("tips"),
                "source_url": payload.get("source_url"),
                "source_file": payload.get("source_file"),
                "text": payload.get("text"),
            }
        )

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
Địa chỉ: {item.get("address")}
Thời điểm phù hợp: {item.get("best_time")}
Ngân sách: {item.get("budget")}
Lưu ý: {item.get("tips")}
Nguồn file: {item.get("source_file")}
Nội dung: {item.get("text")}
Độ liên quan: {item.get("score")}
""".strip()

        if current_length + len(block) > settings.RAG_MAX_CONTEXT_CHARS:
            break

        formatted.append(block)
        current_length += len(block)

    return "\n\n".join(formatted)