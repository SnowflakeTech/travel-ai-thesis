import re
import unicodedata


def clean_text(value: object) -> str:
    if value is None:
        return ""

    text = str(value)
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u200b", "")
    text = text.replace("\ufeff", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_list(value: object) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]

    if isinstance(value, str):
        parts = re.split(r"[,;|]", value)
        return [clean_text(part) for part in parts if clean_text(part)]

    return []


def normalize_city(city: str) -> str:
    city = clean_text(city).lower()

    mapping = {
        "da lat": "đà lạt",
        "dalat": "đà lạt",
        "đà lạt": "đà lạt",
        "da nang": "đà nẵng",
        "danang": "đà nẵng",
        "đà nẵng": "đà nẵng",
        "hoi an": "hội an",
        "hoian": "hội an",
        "hội an": "hội an",
        "ha noi": "hà nội",
        "hanoi": "hà nội",
        "hà nội": "hà nội",
    }

    return mapping.get(city, city)


def normalize_category(category: str) -> str:
    category = clean_text(category).lower()

    mapping = {
        "café": "cafe",
        "coffee": "cafe",
        "cà phê": "cafe",
        "tham quan": "tham quan",
        "attraction": "tham quan",
        "food": "ẩm thực",
        "restaurant": "ẩm thực",
        "ăn uống": "ẩm thực",
        "bien": "biển",
        "beach": "biển",
    }

    return mapping.get(category, category)


def normalize_place(raw_place: dict, fallback_city: str = "") -> dict:
    city = clean_text(raw_place.get("city")) or fallback_city

    place = {
        "title": clean_text(raw_place.get("title")),
        "city": clean_text(city),
        "city_normalized": normalize_city(city),
        "category": clean_text(raw_place.get("category")),
        "category_normalized": normalize_category(raw_place.get("category")),
        "address": clean_text(raw_place.get("address")),
        "best_time": clean_text(raw_place.get("best_time")),
        "budget": clean_text(raw_place.get("budget")),
        "suitable_for": normalize_list(raw_place.get("suitable_for")),
        "description": clean_text(raw_place.get("description")),
        "tips": clean_text(raw_place.get("tips")),
        "source_url": clean_text(raw_place.get("source_url")),
        "latitude": raw_place.get("latitude"),
        "longitude": raw_place.get("longitude"),
    }

    return place


def is_valid_place(place: dict) -> bool:
    required_fields = ["title", "city", "category", "description"]
    return all(clean_text(place.get(field)) for field in required_fields)