from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.rental_service import rental_service

router = APIRouter()

@router.get("/", response_model=List[schemas.Rental])
def read_rentals(
    db: Session = Depends(deps.get_db),
    skip: int = 0,    
    limit: int = 100, 
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Recupera aluguéis do usuário logado.
    """
    rentals = db.query(models.Rental).join(models.Property).filter(
        models.Property.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return rentals

@router.post("/", response_model=schemas.Rental)
def create_rental(
    *,
    db: Session = Depends(deps.get_db),
    rental_in: schemas.RentalCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Cria novo aluguel, validando propriedade do usuário.
    """
    rental = rental_service.create_rental(db=db, rental_in=rental_in, owner_id=current_user.id)
    return rental

@router.get("/{id}", response_model=schemas.Rental)
def read_rental(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Busca um aluguel pelo ID.
    """
    rental = db.query(models.Rental).filter(models.Rental.id == id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Aluguel não encontrado")
    
    # Needs to check property owner
    property_obj = db.query(models.Property).filter(models.Property.id == rental.property_id).first()
    if property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")
        
    return rental

@router.put("/{id}", response_model=schemas.Rental)
def update_rental(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    rental_in: schemas.RentalUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Atualiza um aluguel (ex: mudar valor, hóspedes).
    """
    rental = db.query(models.Rental).filter(models.Rental.id == id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Aluguel não encontrado")
    
    property_obj = db.query(models.Property).filter(models.Property.id == rental.property_id).first()
    if property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    update_data = rental_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rental, field, value)
    
    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental