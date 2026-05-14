import asyncio
import json

from app.agents.travel_graph import run_travel_agent


async def main():
    result = await run_travel_agent(
        "Tôi muốn đi Đà Nẵng 1 ngày, thích biển, đi bộ nhẹ nhàng, ngân sách thấp."
    )

    print("=" * 80)
    print("TRIP REQUIREMENTS")
    print(json.dumps(result.get("trip_requirements"), ensure_ascii=False, indent=2))

    print("=" * 80)
    print("RETRIEVED CONTEXTS")
    for item in result.get("retrieved_contexts", []):
        print(item.get("title"), "-", item.get("city"), "-", item.get("category"))

    print("=" * 80)
    print("ROUTE PLAN")
    print(json.dumps(result.get("route_plan"), ensure_ascii=False, indent=2))

    print("=" * 80)
    print("BUDGET PLAN")
    print(json.dumps(result.get("budget_plan"), ensure_ascii=False, indent=2))

    print("=" * 80)
    print("FINAL ANSWER")
    print(result.get("final_answer"))


if __name__ == "__main__":
    asyncio.run(main())