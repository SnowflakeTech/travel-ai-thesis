from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.db_health import router as db_health_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes.chat import router as chat_router
from app.api.routes.agent import router as agent_router
from app.api.routes.memory import router as memory_router

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
app.include_router(chat_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(memory_router, prefix="/api")