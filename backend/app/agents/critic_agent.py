from typing import Any

from google.genai import types

from app.agents.state import TravelAgentState
from app.ai.gemini_client import client
from app.core.config import settings


def compact_contexts(
    contexts: list[dict[str, Any]],
    max_items: int = 10,
) -> list[dict[str, Any]]:
    compacted = []

    for item in contexts[:max_items]:
        compacted.append(
            {
                "title": item.get("title"),
                "category": item.get("category"),
                "address": item.get("address"),
                "best_time": item.get("best_time"),
                "budget": item.get("budget"),
                "tips": item.get("tips"),
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
    route_plan = compact_route_plan(state.get("route_plan", {}))
    budget_plan = state.get("budget_plan", {})

    prompt = f"""
Bạn là Critic Agent trong hệ thống AI Travel Planner.

Nhiệm vụ:
Tạo câu trả lời cuối cùng cho người dùng dựa trên dữ liệu đã được cung cấp.

DANH SÁCH TÊN ĐƯỢC PHÉP SỬ DỤNG:
{available_titles}

DANH SÁCH NHÓM DỮ LIỆU HIỆN CÓ:
{available_categories}

QUY TẮC BẮT BUỘC:
1. Chỉ sử dụng địa điểm, món ăn, trải nghiệm có trong DANH SÁCH TÊN ĐƯỢC PHÉP SỬ DỤNG hoặc trong retrieved_contexts.
2. Tuyệt đối không tự thêm món ăn, địa điểm, quán, bãi biển, cafe, hoạt động hoặc điểm tham quan không có trong retrieved_contexts.
3. Cá nhân hóa lịch trình dựa trên user_memories nếu phù hợp với yêu cầu người dùng.
4. Không bịa giá vé, giờ mở cửa, tình trạng đông khách, thời gian di chuyển chính xác hoặc dữ liệu thời gian thực.
5. Nếu route_provider là haversine_fallback, chỉ nhắc ngắn rằng khoảng cách là ước lượng.
6. Không viết mở đầu dài.
7. Không lặp lại cùng một lưu ý nhiều lần.
8. Không dùng câu chung chung như "các điểm cảnh đẹp khác", "những địa điểm nổi tiếng khác", "khám phá thêm" nếu không nêu được tên cụ thể từ retrieved_contexts.
9. Nếu có dữ liệu category "lịch trình" hoặc "lịch trình mẫu", hãy dùng nó làm khung chính cho lịch trình.
10. Nếu retrieved_contexts có các mục dạng "Ngày 1", "Ngày 2", "Ngày 3", hãy ưu tiên phân bổ theo đúng thứ tự ngày đó.
11. Nếu route_plan có ordered_places, hãy tham khảo thứ tự điểm đến trong ordered_places, nhưng không cần nhắc chi tiết kỹ thuật.
12. Nếu có dữ liệu ẩm thực, chỉ đưa vào phần ăn uống bổ sung theo từng ngày hoặc phần đặc sản; không biến toàn bộ lịch trình thành food tour trừ khi người dùng chỉ hỏi về ăn uống.
13. Nếu không thấy một món ăn trong retrieved_contexts, không được liệt kê món đó trong phần đặc sản.
14. Nếu không thấy một địa điểm trong retrieved_contexts, không được đưa địa điểm đó vào lịch trình.
15. Nếu dữ liệu không đủ để lập lịch trình chi tiết, hãy nói rõ dữ liệu hiện có còn hạn chế và chỉ gợi ý dựa trên các mục đã truy xuất được.

QUY TẮC DÙNG MEMORY:
1. Nếu user_memories có sở thích liên quan như cafe chill, thiên nhiên, biển, văn hóa, ẩm thực, ít đi bộ, ngân sách thấp, hãy ưu tiên khi chọn và diễn giải lịch trình.
2. Nếu user_memories mâu thuẫn với yêu cầu hiện tại, ưu tiên yêu cầu hiện tại của người dùng.
3. Không nhắc lại toàn bộ memory một cách máy móc.
4. Chỉ dùng memory để cá nhân hóa lựa chọn, nhịp lịch trình, lưu ý và ngân sách.
5. Không tự thêm địa điểm hoặc món ăn chỉ vì memory có nhắc đến, nếu retrieved_contexts không có dữ liệu đó.

QUY TẮC LẬP LỊCH TRÌNH THEO NHU CẦU:
1. Với yêu cầu road trip, thiên nhiên hoặc khám phá:
   - Ưu tiên category "lịch trình", "thiên nhiên", "trải nghiệm", "văn hóa".
   - Ẩm thực chỉ là phần bổ sung theo ngày hoặc phần đặc sản.
2. Với yêu cầu biển:
   - Ưu tiên category "biển" và các điểm có mô tả liên quan đến biển, đi dạo, ngắm cảnh, thư giãn.
3. Với yêu cầu cafe hoặc chill:
   - Ưu tiên category "cafe", địa điểm nhẹ nhàng, thời điểm phù hợp và trải nghiệm thư giãn.
4. Với yêu cầu văn hóa hoặc lịch sử:
   - Ưu tiên category "văn hóa", "tham quan", phố cổ, di tích, bản làng hoặc công trình lịch sử.
5. Với yêu cầu ẩm thực:
   - Ưu tiên category "ẩm thực", nhưng vẫn không được tự thêm món ngoài retrieved_contexts.
6. Với yêu cầu ngân sách thấp:
   - Ưu tiên các mục có budget miễn phí, tùy chọn linh hoạt hoặc chi phí thấp nếu dữ liệu có nêu.
7. Với yêu cầu ít đi bộ hoặc nhẹ nhàng:
   - Không đề xuất trekking dài, lịch trình dày hoặc di chuyển quá nhiều điểm trong một ngày.

QUY TẮC PHÂN BỔ THEO NGÀY:
1. Nếu có lịch trình mẫu, dùng lịch trình mẫu làm khung chính.
2. Nếu không có lịch trình mẫu, tự chia ngày dựa trên best_time, address, category và mức độ phù hợp.
3. Mỗi ngày nên có điểm chính, trải nghiệm phụ và gợi ý ăn uống nếu có dữ liệu.
4. Không nhồi quá nhiều địa điểm vào một ngày.
5. Ngày cuối nên ưu tiên di chuyển nhẹ, kết thúc hành trình hoặc mua đặc sản nếu có dữ liệu phù hợp.

ĐỘ DÀI TỐI ĐA:
- Phần tóm tắt nhu cầu tối đa 2 câu.
- Mỗi ngày tối đa 3 gạch đầu dòng.
- Mỗi gạch đầu dòng tối đa 1 câu.
- Phần đặc sản địa phương tối đa 5 gạch đầu dòng.
- Phần ngân sách tối đa 3 gạch đầu dòng.
- Phần lưu ý tối đa 3 gạch đầu dòng.

ĐỊNH DẠNG TRẢ LỜI:
1. Tóm tắt nhu cầu
2. Lịch trình theo ngày
3. Gợi ý đặc sản địa phương hoặc trải nghiệm phù hợp nếu có dữ liệu
4. Ngân sách tham khảo
5. Lưu ý quan trọng

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

Hãy trả lời bằng tiếng Việt, thực tế, gọn, cụ thể và hoàn chỉnh.
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

    return {
        **state,
        "critique": "Đã kiểm tra lịch trình theo RAG context, route plan, budget plan và user memory.",
        "final_answer": response.text or "",
    }