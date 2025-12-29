from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExpenseBase(BaseModel):
    property_id: int
    expense_title: str
    category: str  
    amount: float
    pay_date: datetime
    description: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    expense_title: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    pay_date: Optional[datetime] = None # type: ignore
    description: Optional[str] = None

class Expense(ExpenseBase):
    id: int
    created_at: Optional[datetime] = None 

    class Config:
        from_attributes = True