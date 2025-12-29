from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.rental_service import rental_service # <--- Importante

router = APIRouter()


@router.get("/", response_model=List[schemas.Rental])
def read_rentals(
    db: Session = Depends(deps.get_db),
    skip: int = 0,    
    limit: int = 100, 
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Recupera aluguéis.
    """
    rentals = crud.rental.get_multi(db=db, skip=skip, limit=limit)
    return rentals


@router.post("/", response_model=schemas.Rental)
def create_rental(
    *,
    db: Session = Depends(deps.get_db),
    rental_in: schemas.RentalCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Cria novo aluguel.
    A lógica de cálculo de preço e validação está dentro do rental_service.
    """
    rental = rental_service.create_rental(db=db, rental_in=rental_in)
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
    rental = crud.rental.get(db=db, id=id)
    if not rental:
        raise HTTPException(status_code=404, detail="Aluguel não encontrado")
    
    
    if not crud.user.is_superuser(current_user) and (rental.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Sem permissão")
        
    return rental