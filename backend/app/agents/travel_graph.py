from langgraph.graph import END, START, StateGraph

from app.agents.budget_agent import budget_agent
from app.agents.critic_agent import critic_agent
from app.agents.planner_agent import planner_agent
from app.agents.retrieval_agent import retrieval_agent
from app.agents.route_agent import route_agent
from app.agents.state import TravelAgentState


def build_travel_graph():
    graph = StateGraph(TravelAgentState)

    graph.add_node("planner", planner_agent)
    graph.add_node("retriever", retrieval_agent)
    graph.add_node("route", route_agent)
    graph.add_node("budget", budget_agent)
    graph.add_node("critic", critic_agent)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "route")
    graph.add_edge("route", "budget")
    graph.add_edge("budget", "critic")
    graph.add_edge("critic", END)

    return graph.compile()


travel_agent_graph = build_travel_graph()


async def run_travel_agent(
    user_request: str,
    user_id: str = "demo_user",
    user_memories: str = "Chưa có thông tin ghi nhớ về người dùng.",
) -> TravelAgentState:
    result = await travel_agent_graph.ainvoke(
        {
            "user_request": user_request,
            "user_id": user_id,
            "user_memories": user_memories,
        }
    )

    return result