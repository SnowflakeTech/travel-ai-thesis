import re
from typing import Any


FORBIDDEN_REALTIME_PATTERNS = [
    r"\bđang mở cửa\b",
    r"\bđang đóng cửa\b",
    r"\bhiện đang đông\b",
    r"\bhiện không đông\b",
    r"\bgiá vé chính xác\b",
    r"\bgiá hiện tại\b",
    r"\bchắc chắn còn phòng\b",
    r"\bđảm bảo\b",
    r"\bchắc chắn\b",
    r"\bcam kết\b",
]

MONEY_PATTERN = re.compile(
    r"(\d{1,3}(?:[.,]\d{3})+|\d+)\s*(vnd|vnđ|đồng|k|nghìn|triệu)",
    flags=re.IGNORECASE,
)

PRICE_KEYWORDS = [
    "giá",
    "giá vé",
    "vé",
    "chi phí",
    "ngân sách",
    "gửi xe",
    "phí",
    "dao động",
    "khoảng",
]

DEFAULT_REALTIME_NOTICE = (
    "Một số thông tin thời gian thực như giá vé, giờ mở cửa, tình trạng đông khách "
    "hoặc tình trạng còn phòng cần được kiểm tra lại từ nguồn chính thức trước khi sử dụng."
)

NO_CONTEXT_NOTICE = (
    "Hệ thống hiện chưa có đủ dữ liệu du lịch phù hợp trong kho tri thức, "
    "vì vậy hệ thống không tạo lịch trình chi tiết để tránh bịa thông tin."
)

ROUTE_ESTIMATE_NOTICE = (
    "Khoảng cách và thời gian di chuyển chỉ là ước lượng theo dữ liệu hiện có, "
    "chưa phải tuyến đường thực tế."
)


def find_forbidden_realtime_claims(answer: str) -> list[str]:
    violations: list[str] = []

    if not answer:
        return violations

    answer_lower = answer.lower()

    for pattern in FORBIDDEN_REALTIME_PATTERNS:
        if re.search(pattern, answer_lower):
            violations.append(pattern)

    return violations


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def is_money_line_allowed(
    line: str,
    allowed_budget_texts: list[str] | None,
) -> bool:
    if not MONEY_PATTERN.search(line):
        return True

    line_lower = normalize_text(line)
    allowed_budget_texts = allowed_budget_texts or []

    for budget in allowed_budget_texts:
        budget_lower = normalize_text(budget)

        if not budget_lower:
            continue

        if budget_lower in line_lower or line_lower in budget_lower:
            return True

    if "miễn phí" in line_lower:
        return True

    return False


def remove_untrusted_price_lines(
    answer: str,
    allowed_budget_texts: list[str] | None,
) -> tuple[str, list[str]]:
    if not answer:
        return answer, []

    cleaned_lines = []
    removed_lines = []

    for line in answer.splitlines():
        line_lower = normalize_text(line)
        has_price_keyword = any(keyword in line_lower for keyword in PRICE_KEYWORDS)
        has_money = MONEY_PATTERN.search(line) is not None

        if has_price_keyword and has_money:
            if not is_money_line_allowed(line, allowed_budget_texts):
                removed_lines.append(line.strip())
                continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip(), removed_lines


def normalize_route_notice(notice: str) -> str:
    notice_lower = notice.lower()

    if "haversine" in notice_lower or "ước lượng theo đường thẳng" in notice_lower:
        return ROUTE_ESTIMATE_NOTICE

    return notice.strip()


def build_safety_notices(
    violations: list[str],
    grounding_guard: dict[str, Any] | None,
    removed_price_lines: list[str] | None = None,
) -> list[str]:
    grounding_guard = grounding_guard or {}
    removed_price_lines = removed_price_lines or []

    notices: list[str] = []

    has_context = grounding_guard.get("has_retrieved_contexts", True)
    is_route_estimate_only = grounding_guard.get("is_route_estimate_only", False)
    warnings = grounding_guard.get("warnings", [])

    if violations:
        notices.append(DEFAULT_REALTIME_NOTICE)

    if removed_price_lines:
        notices.append(
            "Một số dòng có con số chi phí không xuất hiện trong dữ liệu nguồn đã được loại bỏ để tránh bịa giá."
        )

    if not has_context:
        notices.append(NO_CONTEXT_NOTICE)

    if is_route_estimate_only:
        notices.append(ROUTE_ESTIMATE_NOTICE)

    for warning in warnings:
        if isinstance(warning, str) and warning.strip():
            notices.append(normalize_route_notice(warning))

    unique_notices: list[str] = []
    seen = set()

    for notice in notices:
        normalized = normalize_text(notice)

        if normalized not in seen:
            unique_notices.append(notice)
            seen.add(normalized)

    return unique_notices


def answer_has_data_notice(answer: str) -> bool:
    answer_lower = answer.lower()

    return (
        "lưu ý về dữ liệu" in answer_lower
        or "lưu ý dữ liệu" in answer_lower
        or "## lưu ý" in answer_lower
    )


def append_safety_notices(answer: str, notices: list[str]) -> str:
    if not notices:
        return answer.strip()

    if answer_has_data_notice(answer):
        return answer.strip()

    notice_text = "\n\n## Lưu ý về dữ liệu\n" + "\n".join(
        f"- {notice}" for notice in notices[:3]
    )

    return answer.strip() + notice_text


def sanitize_haversine_wording(answer: str) -> str:
    replacements = {
        "Haversine fallback": "ước lượng theo đường thẳng",
        "haversine_fallback": "ước lượng theo đường thẳng",
        "Haversine": "ước lượng theo đường thẳng",
        "Qdrant": "kho tri thức",
        "RAG": "dữ liệu truy xuất",
    }

    sanitized = answer

    for old, new in replacements.items():
        sanitized = sanitized.replace(old, new)

    return sanitized


def sanitize_final_answer(
    answer: str,
    grounding_guard: dict[str, Any] | None = None,
    allowed_budget_texts: list[str] | None = None,
) -> dict[str, Any]:
    answer = answer or ""

    grounding_guard = grounding_guard or {}

    if grounding_guard.get("has_retrieved_contexts") is False:
        violations = find_forbidden_realtime_claims(answer)
        cleaned_answer = sanitize_haversine_wording(answer)

        notices = build_safety_notices(
            violations=violations,
            grounding_guard=grounding_guard,
            removed_price_lines=[],
        )

        sanitized_answer = append_safety_notices(
            answer=cleaned_answer,
            notices=notices,
        )

        return {
            "answer": sanitized_answer,
            "violations": violations,
            "safety_notice_added": sanitized_answer != answer,
            "notices": notices,
            "removed_items": [],
            "warnings": notices,
            "blocked_items": [],
        }

    answer_without_untrusted_prices, removed_price_lines = remove_untrusted_price_lines(
        answer=answer,
        allowed_budget_texts=allowed_budget_texts,
    )

    cleaned_answer = sanitize_haversine_wording(answer_without_untrusted_prices)

    violations = find_forbidden_realtime_claims(cleaned_answer)

    notices = build_safety_notices(
        violations=violations,
        grounding_guard=grounding_guard,
        removed_price_lines=removed_price_lines,
    )

    sanitized_answer = append_safety_notices(
        answer=cleaned_answer,
        notices=notices,
    )

    return {
        "answer": sanitized_answer,
        "violations": violations,
        "safety_notice_added": sanitized_answer != answer,
        "notices": notices,
        "removed_items": removed_price_lines,
        "warnings": notices,
        "blocked_items": removed_price_lines,
    }