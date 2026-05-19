from typing import Any


SUPPORTED_DESTINATIONS = {
    "hà giang",
    "ha giang",
    "hagiang",
    "hội an",
    "hoi an",
    "hoian",
    "hà nội",
    "ha noi",
    "hanoi",
    "đà nẵng",
    "da nang",
    "danang",
    "đà lạt",
    "da lat",
    "dalat",
}


UNSUPPORTED_DESTINATION_KEYWORDS = {
    "iceland": "Iceland",
    "nhật bản": "Nhật Bản",
    "japan": "Nhật Bản",
    "hàn quốc": "Hàn Quốc",
    "korea": "Hàn Quốc",
    "thái lan": "Thái Lan",
    "thailand": "Thái Lan",
    "singapore": "Singapore",
    "paris": "Paris",
    "france": "Pháp",
    "pháp": "Pháp",
    "italy": "Ý",
    "ý": "Ý",
    "switzerland": "Thụy Sĩ",
    "thụy sĩ": "Thụy Sĩ",
}


def normalize_text(text: str) -> str:
    return text.lower().strip()


def detect_requested_destination(user_request: str) -> str | None:
    normalized = normalize_text(user_request)

    for keyword, destination in UNSUPPORTED_DESTINATION_KEYWORDS.items():
        if keyword in normalized:
            return destination

    for destination in SUPPORTED_DESTINATIONS:
        if destination in normalized:
            return destination

    return None


def is_supported_destination(destination: str | None) -> bool:
    if not destination:
        return True

    normalized = normalize_text(destination)

    return normalized in SUPPORTED_DESTINATIONS


def check_destination_support(user_request: str) -> dict[str, Any]:
    requested_destination = detect_requested_destination(user_request)
    supported = is_supported_destination(requested_destination)

    return {
        "requested_destination": requested_destination,
        "is_supported": supported,
        "supported_destinations": [
            "Hà Giang",
            "Hội An",
            "Hà Nội",
            "Đà Nẵng",
            "Đà Lạt",
        ],
    }