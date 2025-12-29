from typing import List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate

class CRUDExpense(CRUDBase[Expense, ExpenseCreate, ExpenseUpdate]):
    
    def get_by_property(
        self, db: Session, *, property_id: int, skip: int = 0, limit: int = 100
    ) -> List[Expense]:
        return (
            db.query(self.model)
            .filter(Expense.property_id == property_id)
            .order_by(Expense.date.desc()) 
            .offset(skip)
            .limit(limit)
            .all()
        )

expense = CRUDExpense(Expense)