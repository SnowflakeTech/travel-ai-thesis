from app.agents.state import TravelAgentState


def budget_agent(state: TravelAgentState) -> TravelAgentState:
    requirements = state.get("trip_requirements", {})
    contexts = state.get("retrieved_contexts", [])

    user_budget = requirements.get("budget_vnd")

    place_budget_notes = []

    for item in contexts:
        place_budget_notes.append(
            {
                "title": item.get("title"),
                "budget": item.get("budget"),
                "category": item.get("category"),
            }
        )

    budget_plan = {
        "user_budget_vnd": user_budget,
        "place_budget_notes": place_budget_notes,
        "assessment": (
            "Ngân sách được đánh giá dựa trên dữ liệu mô tả trong knowledge base. "
            "Hệ thống không khẳng định giá hiện tại nếu dữ liệu không có nguồn thời gian thực."
        ),
    }

    return {
        "budget_plan": budget_plan,
    }