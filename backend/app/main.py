from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.db_health import router as db_health_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.logging import setup_logging


setup_logging()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(db_health_router, prefix="/api")