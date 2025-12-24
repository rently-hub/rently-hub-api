from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str
    DATABASE_URL: str
    SECRET_KEY: str # Usado para assinar o JWT

    class Config:
        env_file = ".env"

settings = Settings()