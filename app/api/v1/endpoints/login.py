from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
import secrets

from app import crud, schemas
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()

@router.post("/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

class GoogleLoginRequest(BaseModel):
    token: str

@router.post("/google", response_model=schemas.Token)
def login_google(
    request: GoogleLoginRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Login with Google token
    """
    try:
        client_id = getattr(settings, "GOOGLE_CLIENT_ID", None)
        idinfo = id_token.verify_oauth2_token(request.token, requests.Request(), client_id)
        
        email = idinfo.get("email")
        name = idinfo.get("name")
        
        if not email:
            raise HTTPException(status_code=400, detail="E-mail não fornecido pelo Google")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Token do Google inválido")

    user = crud.user.get_by_email(db, email=email)
    
    if not user:
        # Create user with a random password
        random_password = secrets.token_urlsafe(32)
        user_in = schemas.UserCreate(
            email=email,
            password=random_password,
            full_name=name or email.split("@")[0],
            is_active=True
        )
        user = crud.user.create(db, obj_in=user_in)
        
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }