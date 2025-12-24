from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Property])
def read_properties(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Recuperar propriedades do próprio usuário logado.
    """
    # CODIGO CORRIGIDO: Removemos o if/else do superuser
    properties = crud.property.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return properties

@router.put("/{id}", response_model=schemas.Property)
def update_property(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    property_in: schemas.PropertyUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Atualizar uma propriedade existente.
    """
    property = crud.property.get(db=db, id=id)
    if not property:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    if property.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Permissões insuficientes") # 403 Forbidden é melhor, mas 400 serve
    
    property = crud.property.update(db=db, db_obj=property, obj_in=property_in)
    return property

@router.post("/", response_model=schemas.Property)
def create_property(
    *,
    db: Session = Depends(deps.get_db),
    property_in: schemas.PropertyCreate,
    current_user: models.User = Depends(deps.get_current_user), # <--- Rota Protegida
) -> Any:
    """
    Criar nova propriedade.
    """
    property = crud.property.create_with_owner(
        db=db, obj_in=property_in, owner_id=current_user.id
    )
    return property

@router.delete("/{id}", response_model=schemas.Property)
def delete_property(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Deletar uma propriedade.
    """
    property = crud.property.get(db=db, id=id)
    if not property:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    if property.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Permissões insuficientes")
    
    property = crud.property.remove(db=db, id=id)
    return property