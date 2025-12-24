from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine
from app.db.base import Base  # Importante para que os models sejam registados

# Cria as tabelas no banco de dados (A "migração" automática inicial)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Bem-vindo ao RentlyHub API", "docs": "/docs"}