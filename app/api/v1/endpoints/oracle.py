from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.services.oracle_service import oracle_service

router = APIRouter()

@router.post("/chat", response_model=schemas.ChatResponse)
async def chat_with_oracle(
    *,
    db: Session = Depends(deps.get_db),
    chat_in: schemas.ChatRequest,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Conversar com o Oráculo RentlyHub.
    """
    response_text = await oracle_service.chat(
        db=db, 
        user_id=current_user.id, 
        message=chat_in.message
    )
    
    return schemas.ChatResponse(response=response_text)
