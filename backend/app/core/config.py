from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Travel AI Thesis"
    APP_ENV: str = "development"

    DATABASE_URL: str
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.4
    GEMINI_MAX_OUTPUT_TOKENS: int = 700
    GEMINI_THINKING_BUDGET: int = 0

    CHAT_MAX_INPUT_CHARS: int = 1200

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "travel_knowledge"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_VECTOR_SIZE: int = 1024

    RAG_TOP_K: int = 5
    RAG_MAX_CONTEXT_CHARS: int = 4500
    RAG_SCORE_THRESHOLD: float = 0.35

    ORS_API_KEY: str = ""
    ORS_BASE_URL: str = "https://api.heigit.org/openrouteservice"

    NOMINATIM_BASE_URL: str = "https://nominatim.openstreetmap.org"
    NOMINATIM_USER_AGENT: str = "travel-ai-thesis-student-project/1.0"

    ROUTE_PROVIDER: str = "ors"
    ROUTE_PROFILE: str = "foot-walking"
    ROUTE_MAX_PLACES: int = 6
    ROUTE_CACHE_DIR: str = ".cache/routes"

    MEMORY_MAX_ITEMS: int = 20
    MEMORY_EXTRACTION_MAX_OUTPUT_TOKENS: int = 500
    MEMORY_ENABLE_LLM_EXTRACTION: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()