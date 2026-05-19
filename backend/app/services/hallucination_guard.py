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


DEFAULT_REALTIME_NOTICE = (
    "Một số thông tin thời gian thực như giá vé, giờ mở cửa, tình trạng đông khách "
    "hoặc tình trạng còn phòng cần được kiểm tra lại từ nguồn chính thức trước khi sử dụng."
)

NO_CONTEXT_NOTICE = (
    "Hệ thống hiện chưa có đủ dữ liệu du lịch phù hợp trong kho tri thức, "
    "vì vậy gợi ý trên chỉ nên xem là tham khảo."
)

ROUTE_ESTIMATE_NOTICE = (
    "Khoảng cách và thời gian di chuyển chỉ là ước lượng theo dữ liệu hiện có, "
    "chưa phải tuyến đường thực tế."
)


def find_forbidden_realtime_claims(answer: str) -> list[str]:
    """
    Tìm các cụm từ có nguy cơ tạo cảm giác thông tin thời gian thực hoặc cam kết tuyệt đối.
    """
    violations: list[str] = []

    if not answer:
        return violations

    answer_lower = answer.lower()

    for pattern in FORBIDDEN_REALTIME_PATTERNS:
        if re.search(pattern, answer_lower):
            violations.append(pattern)

    return violations


def build_safety_notices(
    violations: list[str],
    grounding_guard: dict[str, Any] | None,
) -> list[str]:
    """
    Gom toàn bộ cảnh báo cần thêm vào câu trả lời cuối.
    """
    grounding_guard = grounding_guard or {}

    notices: list[str] = []

    has_context = grounding_guard.get("has_retrieved_contexts", True)
    is_route_estimate_only = grounding_guard.get("is_route_estimate_only", False)
    warnings = grounding_guard.get("warnings", [])

    if violations:
        notices.append(DEFAULT_REALTIME_NOTICE)

    if not has_context:
        notices.append(NO_CONTEXT_NOTICE)

    if is_route_estimate_only:
        notices.append(ROUTE_ESTIMATE_NOTICE)

    for warning in warnings:
        if isinstance(warning, str) and warning.strip():
            notices.append(warning.strip())

    # Loại trùng cảnh báo nhưng vẫn giữ thứ tự
    unique_notices: list[str] = []
    for notice in notices:
        if notice not in unique_notices:
            unique_notices.append(notice)

    return unique_notices


def append_safety_notices(answer: str, notices: list[str]) -> str:
    """
    Thêm phần lưu ý vào cuối câu trả lời.
    Chỉ thêm nếu câu trả lời chưa có mục 'Lưu ý về dữ liệu'.
    """
    if not notices:
        return answer

    if "## Lưu ý về dữ liệu" in answer:
        return answer

    notice_text = "\n\n## Lưu ý về dữ liệu\n" + "\n".join(
        f"- {notice}" for notice in notices
    )

    return answer.strip() + notice_text


def sanitize_final_answer(
    answer: str,
    grounding_guard: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Post-processing guard cho câu trả lời cuối của Agent.

    Chức năng:
    1. Phát hiện các claim dễ gây hallucination về dữ liệu thời gian thực.
    2. Thêm cảnh báo nếu route chỉ là ước lượng.
    3. Thêm cảnh báo nếu thiếu retrieved contexts.
    4. Trả về câu trả lời đã được bổ sung safety notice.
    """
    answer = answer or ""

    violations = find_forbidden_realtime_claims(answer)
    notices = build_safety_notices(
        violations=violations,
        grounding_guard=grounding_guard,
    )

    sanitized_answer = append_safety_notices(
        answer=answer,
        notices=notices,
    )

    return {
        "answer": sanitized_answer,
        "violations": violations,
        "safety_notice_added": sanitized_answer != answer,
        "notices": notices,
    }