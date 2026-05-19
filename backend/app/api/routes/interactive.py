from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.travel_graph import run_travel_agent
from app.core.security import verify_demo_api_key
from app.db.session import get_db
from app.memory.service import get_user_memory_text, save_or_update_memory


router = APIRouter(dependencies=[Depends(verify_demo_api_key)])


class RegenerateDayRequest(BaseModel):
    user_id: str = "demo_user"
    day: int
    original_request: str


class OptimizeRouteRequest(BaseModel):
    user_id: str = "demo_user"
    original_request: str


class PreferencesRequest(BaseModel):
    travelStyle: str = ""
    budgetLevel: str = ""
    walkingLevel: str = ""
    favoritePlaces: str = ""
    avoidPlaces: str = ""


@router.post("/agent/regenerate-day")
async def regenerate_day(
    request: RegenerateDayRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user_memory_text = await get_user_memory_text(
            db=db,
            user_id=request.user_id,
        )

        new_request = f"""
Người dùng muốn tạo lại riêng ngày {request.day} trong lịch trình.

Yêu cầu gốc:
{request.original_request}

Yêu cầu mới:
- Giữ đúng thành phố, thời lượng và phong cách chính.
- Chỉ đề xuất phương án khác cho ngày {request.day}.
- Không làm lịch trình quá dày.
- Nếu có memory người dùng, hãy cá nhân hóa theo memory.
""".strip()

        result = await run_travel_agent(
            user_request=new_request,
            user_id=request.user_id,
            user_memories=user_memory_text,
        )

        return {
            "answer": result.get("final_answer", ""),
            "route_plan": result.get("route_plan", {}),
            "budget_plan": result.get("budget_plan", {}),
            "grounding_guard": result.get("grounding_guard", {}),
            "post_processing_guard": result.get("post_processing_guard", {}),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Regenerate day error: {str(exc)}",
        )


@router.post("/agent/optimize-route")
async def optimize_route(
    request: OptimizeRouteRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user_memory_text = await get_user_memory_text(
            db=db,
            user_id=request.user_id,
        )

        new_request = f"""
Yêu cầu gốc:
{request.original_request}

Hãy tối ưu lại lịch trình theo tiêu chí:
- Giảm di chuyển không cần thiết.
- Nhóm địa điểm gần nhau.
- Tránh lịch trình quá dày.
- Ưu tiên trải nghiệm nhẹ nhàng.
- Nếu có route_plan hoặc dữ liệu tọa độ, hãy tận dụng để sắp xếp hợp lý hơn.
""".strip()

        result = await run_travel_agent(
            user_request=new_request,
            user_id=request.user_id,
            user_memories=user_memory_text,
        )

        return {
            "answer": result.get("final_answer", ""),
            "route_plan": result.get("route_plan", {}),
            "budget_plan": result.get("budget_plan", {}),
            "grounding_guard": result.get("grounding_guard", {}),
            "post_processing_guard": result.get("post_processing_guard", {}),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Optimize route error: {str(exc)}",
        )


@router.post("/preferences/{user_id}")
async def save_user_preferences(
    user_id: str,
    request: PreferencesRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        saved = []

        preferences = [
            ("travel_style", request.travelStyle),
            ("budget_preference", request.budgetLevel),
            ("mobility_constraint", request.walkingLevel),
            ("travel_preference", request.favoritePlaces),
            ("travel_dislike", request.avoidPlaces),
        ]

        for memory_type, content in preferences:
            if content.strip():
                memory = await save_or_update_memory(
                    db=db,
                    user_id=user_id,
                    memory_type=memory_type,
                    content=content.strip(),
                    source_message="manual_preferences_editor",
                    confidence=0.95,
                )

                saved.append(
                    {
                        "id": memory.id,
                        "memory_type": memory.memory_type,
                        "content": memory.content,
                        "confidence": memory.confidence,
                    }
                )

        return {
            "status": "ok",
            "saved": saved,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Save preferences memory error: {str(exc)}",
        )