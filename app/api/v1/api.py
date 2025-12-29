from fastapi import APIRouter
from app.api.v1.endpoints import users, login, properties, rental, expenses
api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"]) 
api_router.include_router(rental.router, prefix="/rentals", tags=["rentals"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])