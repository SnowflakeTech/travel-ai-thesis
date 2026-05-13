from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Travel AI Thesis"
    APP_ENV: str = "development"
    DATABASE_URL: str
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()