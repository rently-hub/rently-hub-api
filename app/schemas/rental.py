from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class RentalBase(BaseModel):
    property_id: int
    start_date: date
    end_date: date 
    guest_count: int
   
class RentalCreate(RentalBase):
    pass

class RentalUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    guest_count: int | None = None
    total_price: float | None = None 
    status: str | None = None 

class Rental(RentalBase):
    id: int
    status: str
    total_price: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True