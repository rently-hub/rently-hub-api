from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.services.property_service import property_service 


router = APIRouter()

@router.get("/", response_model=List[schemas.Property])
def read_properties(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Lista propriedades do usuário logado, JÁ COM O STATUS CALCULADO.
    """
    properties = property_service.get_owner_properties(
        db=db, 
        owner_id=current_user.id, 
        skip=skip, 
        limit=limit
    )
    return properties


@router.get("/{id}", response_model=schemas.PropertyDetail)
def read_property(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    
    property_data = property_service.get_property_details(db=db, id=id)
    
    if not property_data:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
        

    return property_data