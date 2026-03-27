from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RentlyHub" 
    DATABASE_URL: str 
    SECRET_KEY: str 
    GOOGLE_CLIENT_ID: str | None = None


    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()