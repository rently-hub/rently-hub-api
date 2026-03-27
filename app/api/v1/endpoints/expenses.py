from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Expense])
def read_expenses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Recupera lista de despesas do usuário logado.
    """
    expenses = db.query(models.Expense).join(models.Property).filter(
        models.Property.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return expenses

@router.post("/", response_model=schemas.Expense)
def create_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_in: schemas.ExpenseCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Cria nova despesa se a propriedade for do usuário.
    """
    property_obj = crud.property.get(db=db, id=expense_in.property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada.")
    if property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão.")

    expense = crud.expense.create(db=db, obj_in=expense_in)
    return expense

@router.put("/{id}", response_model=schemas.Expense)
def update_expense(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    expense_in: schemas.ExpenseUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Atualiza uma despesa.
    """
    expense = crud.expense.get(db=db, id=id)
    if not expense:
        raise HTTPException(status_code=404, detail="Despesa não encontrada.")
    property_obj = crud.property.get(db=db, id=expense.property_id)
    if not property_obj or property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão.")

    expense = crud.expense.update(db=db, db_obj=expense, obj_in=expense_in)
    return expense

@router.delete("/{id}", response_model=schemas.Expense)
def delete_expense(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Deleta uma despesa.
    """
    expense = crud.expense.get(db=db, id=id)
    if not expense:
        raise HTTPException(status_code=404, detail="Despesa não encontrada.")
    property_obj = crud.property.get(db=db, id=expense.property_id)
    if not property_obj or property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão.")

    expense = crud.expense.remove(db=db, id=id)
    return expense