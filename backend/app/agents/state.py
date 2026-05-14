from typing import Any, TypedDict


class TravelAgentState(TypedDict, total=False):
    user_request: str

    trip_requirements: dict[str, Any]
    retrieved_contexts: list[dict[str, Any]]

    route_plan: dict[str, Any]
    budget_plan: dict[str, Any]

    critique: str
    final_answer: str