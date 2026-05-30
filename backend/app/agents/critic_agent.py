from typing import Any

from google.genai import types

from app.agents.state import TravelAgentState
from app.ai.gemini_client import client
from app.core.config import settings
from app.services.hallucination_guard import sanitize_final_answer


def compact_contexts(
    contexts: list[dict[str, Any]],
    max_items: int = 10,
) -> list[dict[str, Any]]:
    compacted = []

    for item in contexts[:max_items]:
        compacted.append(
            {
                "title": item.get("title"),
                "city": item.get("city"),
                "category": item.get("category"),
                "address": item.get("address"),
                "best_time": item.get("best_time"),
                "budget": item.get("budget"),
                "tips": item.get("tips"),
                "source_url": item.get("source_url"),
                "source_file": item.get("source_file"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "text": item.get("text"),
            }
        )

    return compacted


def compact_route_plan(route_plan: dict[str, Any]) -> dict[str, Any]:
    route_summary = route_plan.get("route_summary", {}) or {}

    return {
        "ordered_places": route_plan.get("ordered_places", []),
        "missing_coordinate_places": route_plan.get("missing_coordinate_places", []),
        "route_provider": route_summary.get("provider"),
        "route_note": route_summary.get("note"),
        "total_distance_km": route_summary.get("total_distance_km"),
        "total_duration_minutes": route_summary.get("total_duration_minutes"),
    }


def extract_available_titles(contexts: list[dict[str, Any]]) -> list[str]:
    titles = []

    for item in contexts:
        title = item.get("title")

        if title and title not in titles:
            titles.append(title)

    return titles


def extract_available_categories(contexts: list[dict[str, Any]]) -> list[str]:
    categories = []

    for item in contexts:
        category = item.get("category")

        if category and category not in categories:
            categories.append(category)

    return categories


def extract_budget_texts(contexts: list[dict[str, Any]]) -> list[str]:
    budget_texts = []

    for item in contexts:
        budget = item.get("budget")

        if isinstance(budget, str) and budget.strip() and budget not in budget_texts:
            budget_texts.append(budget.strip())

    return budget_texts


def build_allowed_place_names(
    grounding_guard: dict[str, Any],
    available_titles: list[str],
) -> list[str]:
    guard_names = grounding_guard.get("allowed_place_names", [])

    if isinstance(guard_names, list) and guard_names:
        return [name for name in guard_names if isinstance(name, str) and name.strip()]

    return available_titles


def build_post_guard_info(
    sanitized: dict[str, Any],
    raw_answer: str,
) -> dict[str, Any]:
    sanitized_answer = sanitized.get("answer", raw_answer)

    return {
        "was_modified": sanitized_answer != raw_answer,
        "removed_items": sanitized.get("removed_items", []),
        "warnings": sanitized.get("warnings", []),
        "blocked_items": sanitized.get("blocked_items", []),
        "violations": sanitized.get("violations", []),
        "safety_notice_added": sanitized.get("safety_notice_added", False),
        "guard_applied": True,
    }


def build_no_context_answer(
    user_request: str,
    grounding_guard: dict[str, Any],
) -> str:
    warnings = grounding_guard.get("warnings", [])

    supported_hint = (
        "Bạn có thể thử lại với các địa phương đã có trong dữ liệu như Đà Lạt, "
        "Đà Nẵng, Hội An, Hà Nội, Hà Giang hoặc Hải Dương."
    )

    if warnings:
        warning_text = "\n".join(f"- {warning}" for warning in warnings)
    else:
        warning_text = "- Không tìm thấy retrieved contexts phù hợp trong kho tri thức."

    return f"""
Hệ thống hiện chưa có đủ dữ liệu phù hợp để tạo lịch trình chi tiết cho yêu cầu này, nên mình sẽ không tự tạo lịch trình để tránh bịa thông tin.

Yêu cầu đã nhận:
{user_request}

Lý do:
{warning_text}

{supported_hint}
""".strip()


async def critic_agent(state: TravelAgentState) -> TravelAgentState:
    user_request = state["user_request"]

    user_memories = state.get(
        "user_memories",
        "Chưa có thông tin ghi nhớ về người dùng.",
    )

    requirements = state.get("trip_requirements", {})
    raw_contexts = state.get("retrieved_contexts", [])
    contexts = compact_contexts(raw_contexts, max_items=10)
    available_titles = extract_available_titles(raw_contexts)
    available_categories = extract_available_categories(raw_contexts)
    available_budget_texts = extract_budget_texts(raw_contexts)
    route_plan = compact_route_plan(state.get("route_plan", {}))
    budget_plan = state.get("budget_plan", {})
    grounding_guard = state.get("grounding_guard", {})

    allowed_place_names = build_allowed_place_names(
        grounding_guard=grounding_guard,
        available_titles=available_titles,
    )

    if not raw_contexts:
        raw_answer = build_no_context_answer(
            user_request=user_request,
            grounding_guard=grounding_guard,
        )

        sanitized = sanitize_final_answer(
            answer=raw_answer,
            grounding_guard=grounding_guard,
            allowed_budget_texts=available_budget_texts,
        )

        post_guard_info = build_post_guard_info(
            sanitized=sanitized,
            raw_answer=raw_answer,
        )

        return {
            **state,
            "critique": "Workflow dừng tạo lịch trình chi tiết vì không có retrieved contexts phù hợp.",
            "final_answer": sanitized.get("answer", raw_answer),
            "post_processing_guard": post_guard_info,
        }

    prompt = f"""
Bạn là Critic Agent trong hệ thống AI Travel Planner.

Nhiệm vụ:
Tạo câu trả lời cuối cùng cho người dùng dựa trên dữ liệu đã được cung cấp.

DANH SÁCH TÊN ĐƯỢC PHÉP SỬ DỤNG:
{allowed_place_names}

DANH SÁCH NHÓM DỮ LIỆU HIỆN CÓ:
{available_categories}

DANH SÁCH NGÂN SÁCH ĐƯỢC PHÉP TRÍCH DẪN:
{available_budget_texts}

QUY TẮC CHỐNG HALLUCINATION BẮT BUỘC:
1. Chỉ được đề xuất các địa điểm, món ăn, trải nghiệm có trong DANH SÁCH TÊN ĐƯỢC PHÉP SỬ DỤNG.
2. Không tự thêm địa điểm mới nếu địa điểm đó không có trong retrieved_contexts.
3. Không bịa giá vé, giờ mở cửa, tình trạng đông khách, thời tiết, kẹt xe hoặc dữ liệu thời gian thực.
4. Nếu dữ liệu không đủ, phải nói rõ: "Hệ thống hiện chưa có đủ dữ liệu để khẳng định chi tiết này."
5. Nếu route_provider là "haversine_fallback", chỉ nói một lần rằng khoảng cách là ước lượng theo đường thẳng, không phải tuyến đường thực tế.
6. Nếu không có retrieved_contexts, không được tạo lịch trình chi tiết như thể đã có dữ liệu.
7. Khi nêu ngân sách, chỉ được dùng đúng nội dung trong DANH SÁCH NGÂN SÁCH ĐƯỢC PHÉP TRÍCH DẪN.
8. Nếu budget trong dữ liệu ghi "Tùy...", "Miễn phí", "Tùy chi phí cá nhân", chỉ được diễn giải ở mức chung, không được tự suy ra số tiền.
9. Không dùng các cụm khẳng định tuyệt đối như "chắc chắn", "đảm bảo", "đang mở cửa", "giá chính xác".
10. Không dùng câu chung chung như "các điểm nổi tiếng khác", "khám phá thêm", "những quán ngon khác" nếu không nêu được tên cụ thể trong retrieved_contexts.
11. Nếu không thấy một món ăn trong retrieved_contexts, không được liệt kê món đó trong phần đặc sản.
12. Nếu không thấy một địa điểm trong retrieved_contexts, không được đưa địa điểm đó vào lịch trình.
13. Nếu có cảnh báo trong grounding_guard, phải tôn trọng cảnh báo đó khi tạo câu trả lời.
14. Không lặp lại phần "Lưu ý về dữ liệu" nhiều lần.

QUY TẮC DÙNG MEMORY:
1. Nếu user_memories có sở thích liên quan như cafe chill, thiên nhiên, biển, văn hóa, ẩm thực, ít đi bộ, ngân sách thấp, hãy ưu tiên khi chọn và diễn giải lịch trình.
2. Nếu user_memories mâu thuẫn với yêu cầu hiện tại, ưu tiên yêu cầu hiện tại của người dùng.
3. Không nhắc lại toàn bộ memory một cách máy móc.
4. Chỉ dùng memory để cá nhân hóa lựa chọn, nhịp lịch trình, lưu ý và ngân sách.
5. Không tự thêm địa điểm hoặc món ăn chỉ vì memory có nhắc đến, nếu retrieved_contexts không có dữ liệu đó.

QUY TẮC LẬP LỊCH TRÌNH THEO NHU CẦU:
1. Với yêu cầu road trip, thiên nhiên hoặc khám phá:
   - Ưu tiên category "lịch trình", "lịch trình mẫu", "thiên nhiên", "trải nghiệm", "văn hóa".
   - Ẩm thực chỉ là phần bổ sung theo ngày hoặc phần đặc sản.
2. Với yêu cầu biển:
   - Ưu tiên category "biển" và các điểm có mô tả liên quan đến biển, đi dạo, ngắm cảnh, thư giãn.
3. Với yêu cầu cafe hoặc chill:
   - Ưu tiên category "cafe", địa điểm nhẹ nhàng, thời điểm phù hợp và trải nghiệm thư giãn.
4. Với yêu cầu văn hóa hoặc lịch sử:
   - Ưu tiên category "văn hóa", "tham quan", "phố cổ", "di tích", "bảo tàng", "di sản".
5. Với yêu cầu ẩm thực:
   - Ưu tiên category "ẩm thực", nhưng vẫn không được tự thêm món ngoài retrieved_contexts.
6. Với yêu cầu ngân sách thấp:
   - Ưu tiên các mục có budget miễn phí, tùy chọn linh hoạt hoặc chi phí thấp nếu dữ liệu có nêu.
7. Với yêu cầu ít đi bộ hoặc nhẹ nhàng:
   - Không đề xuất trekking dài, lịch trình dày hoặc di chuyển quá nhiều điểm trong một ngày.

QUY TẮC PHÂN BỔ THEO NGÀY:
1. Nếu có dữ liệu category "lịch trình" hoặc "lịch trình mẫu", hãy dùng nó làm khung chính cho lịch trình.
2. Nếu retrieved_contexts có các mục dạng "Ngày 1", "Ngày 2", "Ngày 3", hãy ưu tiên phân bổ theo đúng thứ tự ngày đó.
3. Nếu route_plan có ordered_places, hãy tham khảo thứ tự điểm đến trong ordered_places, nhưng không cần nhắc chi tiết kỹ thuật.
4. Nếu không có lịch trình mẫu, tự chia ngày dựa trên best_time, address, category và mức độ phù hợp.
5. Mỗi ngày nên có điểm chính, trải nghiệm phụ và gợi ý ăn uống nếu có dữ liệu.
6. Không nhồi quá nhiều địa điểm vào một ngày.
7. Ngày cuối nên ưu tiên di chuyển nhẹ, kết thúc hành trình hoặc mua đặc sản nếu có dữ liệu phù hợp.

ĐỘ DÀI TỐI ĐA:
- Phần tóm tắt nhu cầu tối đa 2 câu.
- Mỗi ngày tối đa 3 gạch đầu dòng.
- Mỗi gạch đầu dòng tối đa 1 câu.
- Phần đặc sản địa phương tối đa 5 gạch đầu dòng.
- Phần ngân sách tối đa 3 gạch đầu dòng.
- Phần lưu ý tối đa 3 gạch đầu dòng.
- Phần "Lưu ý về dữ liệu" tối đa 3 gạch đầu dòng.

ĐỊNH DẠNG TRẢ LỜI:
1. Tóm tắt nhu cầu
2. Lịch trình theo ngày
3. Gợi ý đặc sản địa phương hoặc trải nghiệm phù hợp nếu có dữ liệu
4. Ngân sách tham khảo
5. Lưu ý quan trọng
6. Lưu ý về dữ liệu nếu có cảnh báo trong grounding_guard hoặc dữ liệu chưa đủ

Thông tin đã ghi nhớ về người dùng:
{user_memories}

Yêu cầu người dùng:
{user_request}

Trip requirements:
{requirements}

Retrieved contexts:
{contexts}

Route plan:
{route_plan}

Budget plan:
{budget_plan}

Grounding guard:
{grounding_guard}

YÊU CẦU ĐẦU RA:
- Trả lời bằng tiếng Việt.
- Có cấu trúc rõ ràng.
- Chỉ có một phần "Lưu ý về dữ liệu" ở cuối nếu cần.
- Không nhắc đến tên kỹ thuật như RAG, Haversine, Qdrant nếu không cần.
- Nếu cần nói về route_provider haversine_fallback, hãy diễn đạt dễ hiểu là: "khoảng cách chỉ là ước lượng theo đường thẳng, không phải tuyến đường thực tế".
- Không đề xuất bất kỳ địa điểm, món ăn, hoạt động hoặc trải nghiệm nào ngoài DANH SÁCH TÊN ĐƯỢC PHÉP SỬ DỤNG.
- Không tự tạo con số ngân sách nếu con số đó không xuất hiện trong retrieved_contexts.
""".strip()

    response = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
            thinking_config=types.ThinkingConfig(
                thinking_budget=settings.GEMINI_THINKING_BUDGET
            ),
        ),
    )

    raw_answer = response.text or ""

    sanitized = sanitize_final_answer(
        answer=raw_answer,
        grounding_guard=grounding_guard,
        allowed_budget_texts=available_budget_texts,
    )

    post_guard_info = build_post_guard_info(
        sanitized=sanitized,
        raw_answer=raw_answer,
    )

    return {
        **state,
        "critique": "Đã kiểm tra lịch trình theo retrieved contexts, route plan, budget plan, user memory và grounding guard.",
        "final_answer": sanitized.get("answer", raw_answer),
        "post_processing_guard": post_guard_info,
    }