from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from app.services.ical_service import sync_property_ical
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
        
    if property_data.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")

    return property_data

@router.post("/", response_model=schemas.Property)
def create_property(
    *,
    db: Session = Depends(deps.get_db),
    property_in: schemas.PropertyCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Cria uma nova propriedade para o usuário logado.
    """
    property_obj = property_service.PropertyCreate(
        db=db, 
        obj_in=property_in, 
        owner_id=current_user.id
    )
    return property_obj     

@router.post("/{id}/sync-ical")
def sync_ical(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    property_obj = db.query(models.Property).filter(models.Property.id == id, models.Property.owner_id == current_user.id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada ou sem permissão")
    
    result = sync_property_ical(db=db, property_id=id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return result

from datetime import date

@router.put("/{id}", response_model=schemas.Property)
def update_property(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    property_in: schemas.PropertyUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Atualiza uma propriedade.
    """
    property_obj = db.query(models.Property).filter(models.Property.id == id, models.Property.owner_id == current_user.id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    
    # Preparamos os dados para atualizar (ignore nulos)
    update_data = property_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(property_obj, field, value)
    
    db.add(property_obj)
    db.commit()
    db.refresh(property_obj)
    return property_obj

@router.delete("/{id}")
def delete_property(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    # 1. Fetch Property
    property_obj = db.query(models.Property).filter(models.Property.id == id, models.Property.owner_id == current_user.id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada ou sem permissão")
    
    # 2. Check if it has any ACTIVE rentals TODAY
    today = date.today()
    active_rental = db.query(models.Rental).filter(
        models.Rental.property_id == id,
        models.Rental.status == "active",
        models.Rental.start_date <= today,
        models.Rental.end_date >= today
    ).first()

    if active_rental:
        raise HTTPException(
            status_code=400, 
            detail=f"Não é possível excluir uma propriedade que está ALUGADA no momento (Reserva #{active_rental.id}). Encerre o aluguel antes de excluir."
        )
    
    # 3. If no active rentals today, delete (cascade will handle the rest)
    db.delete(property_obj)
    db.commit()
    
    return {"message": "Propriedade excluída com sucesso"}