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
        "ha giang": "hà giang",
        "hagiang": "hà giang",
        "hà giang": "hà giang",
    }

    return mapping.get(city, city)


def normalize_category(category: str) -> str:
    category = clean_text(category).lower()

    mapping = {
        "café": "cafe",
        "coffee": "cafe",
        "cà phê": "cafe",
        "cafe": "cafe",
        "tham quan": "tham quan",
        "attraction": "tham quan",
        "attractions": "tham quan",
        "điểm tham quan": "tham quan",
        "food": "ẩm thực",
        "foods": "ẩm thực",
        "restaurant": "ẩm thực",
        "restaurants": "ẩm thực",
        "ăn uống": "ẩm thực",
        "ẩm thực": "ẩm thực",
        "đặc sản": "ẩm thực",
        "món địa phương": "ẩm thực",
        "món ăn địa phương": "ẩm thực",
        "bien": "biển",
        "biển": "biển",
        "beach": "biển",
        "beaches": "biển",
        "nature": "thiên nhiên",
        "thiên nhiên": "thiên nhiên",
        "natural": "thiên nhiên",
        "núi": "thiên nhiên",
        "đèo": "thiên nhiên",
        "sông": "thiên nhiên",
        "thác": "thiên nhiên",
        "hang": "thiên nhiên",
        "culture": "văn hóa",
        "cultural": "văn hóa",
        "văn hóa": "văn hóa",
        "lịch sử": "văn hóa",
        "bản làng": "văn hóa",
        "chợ phiên": "văn hóa",
        "experience": "trải nghiệm",
        "experiences": "trải nghiệm",
        "adventure": "trải nghiệm",
        "adventures": "trải nghiệm",
        "trải nghiệm": "trải nghiệm",
        "phiêu lưu": "trải nghiệm",
        "road trip": "trải nghiệm",
        "trekking": "trải nghiệm",
        "phượt": "trải nghiệm",
        "itinerary": "lịch trình",
        "itineraries": "lịch trình",
        "sample itinerary": "lịch trình",
        "lịch trình": "lịch trình",
        "lịch trình mẫu": "lịch trình",
        "hành trình": "lịch trình",
    }

    return mapping.get(category, category)


def normalize_place(raw_place: dict, fallback_city: str = "") -> dict:
    city = clean_text(raw_place.get("city")) or fallback_city
    category = clean_text(raw_place.get("category"))

    place = {
        "title": clean_text(raw_place.get("title")),
        "city": clean_text(city),
        "city_normalized": normalize_city(city),
        "category": category,
        "category_normalized": normalize_category(category),
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