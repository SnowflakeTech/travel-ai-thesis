from app.agents.state import TravelAgentState
from app.core.config import settings
from app.rag.retriever import retrieve_context


def retrieval_agent(state: TravelAgentState) -> TravelAgentState:
    user_request = state["user_request"]

    contexts = retrieve_context(
        query=user_request,
        limit=settings.RAG_TOP_K,
        use_filter=True,
    )

    return {
        **state,
        "retrieved_contexts": contexts,
    }