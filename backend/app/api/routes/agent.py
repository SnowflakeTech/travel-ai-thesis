from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.travel_graph import run_travel_agent


router = APIRouter()


class AgentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1200)


class AgentResponse(BaseModel):
    answer: str
    trip_requirements: dict[str, Any]
    retrieved_contexts: list[dict[str, Any]]
    route_plan: dict[str, Any]
    budget_plan: dict[str, Any]
    critique: str


@router.post("/agent/travel", response_model=AgentResponse)
async def travel_agent(request: AgentRequest):
    try:
        result = await run_travel_agent(request.message)

        return AgentResponse(
            answer=result.get("final_answer", ""),
            trip_requirements=result.get("trip_requirements", {}),
            retrieved_contexts=result.get("retrieved_contexts", []),
            route_plan=result.get("route_plan", {}),
            budget_plan=result.get("budget_plan", {}),
            critique=result.get("critique", ""),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Travel agent workflow error: {str(exc)}",
        )