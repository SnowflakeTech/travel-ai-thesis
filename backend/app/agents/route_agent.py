from app.agents.state import TravelAgentState
from app.services.route_service import build_route_plan


async def route_agent(state: TravelAgentState) -> TravelAgentState:
    contexts = state.get("retrieved_contexts", [])

    route_plan = await build_route_plan(contexts)

    return {
        "route_plan": route_plan,
    }