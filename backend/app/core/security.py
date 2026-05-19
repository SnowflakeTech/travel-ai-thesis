from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_demo_api_key(
    x_demo_api_key: str | None = Header(default=None),
) -> None:
    """
    Lightweight demo/admin protection.

    Frontend must send:
    x-demo-api-key: <DEMO_API_KEY>
    """

    if not settings.ENABLE_DEMO_AUTH:
        return

    if not settings.DEMO_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DEMO_API_KEY is not configured on backend.",
        )

    if not x_demo_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-demo-api-key header.",
        )

    if x_demo_api_key != settings.DEMO_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid demo API key.",
        )