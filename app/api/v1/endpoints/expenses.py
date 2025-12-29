from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Expense])
def read_expeneses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Recupera lista de despesas.
    """
    expenses = crud.expense.get_multi(db, skip=skip, limit=limit)
    return expenses


@router.post("/", response_model=schemas.Expense)
def create_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_in: schemas.ExpenseCreate,
) -> Any:
    """
    Cria nova despesa.
    """
    property_obj = crud.property.get(db=db, id=expense_in.property_id)
    if not property_obj:
        raise HTTPException(
            status_code=404,
            detail="Propriedade não encontrada.",
        )
    expense = crud.expense.create(db=db, obj_in=expense_in)
    return expense

@router.put("/{id}", response_model=schemas.Expense)
def update_expense(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    expense_in: schemas.ExpenseUpdate,
) -> Any:
    """
    Atualiza uma despesa existente.
    """
    expense = crud.expense.get(db=db, id=id)
    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Despesa não encontrada.",
        )
    expense = crud.expense.update(db=db, db_obj=expense, obj_in=expense_in)
    return expense

@router.delete("/{id}", response_model=schemas.Expense)
def delete_expense(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Deleta uma despesa existente.
    """
    expense = crud.expense.get(db=db, id=id)
    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Despesa não encontrada.",
        )
    expense = crud.expense.remove(db=db, id=id)
    return expense