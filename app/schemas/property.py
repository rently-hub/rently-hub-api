from typing import Optional, List, Any
from pydantic import BaseModel
from app.schemas.expense import Expense
from app.schemas.rental import Rental

# --- BASES ---

class PropertyBase(BaseModel):
    title: str                      
    description: Optional[str] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    price_per_day: float            
    cleaning_fee: Optional[float] = 0.0
    max_guests: int              

class PropertyCreate(PropertyBase):
    pass 

class PropertyUpdate(PropertyBase):    
    title: Optional[str] = None          
    price_per_day: Optional[float] = None
    max_guests: Optional[int] = None

class CurrentRentalInfo(BaseModel):
    rental_id: int
    start_date: Any
    end_date: Any
    total_days: int
    total_price: float
    guest_name: Optional[str] = "Cliente"

class Property(PropertyBase):
    id: int
    owner_id: int

    status: str = "Disponível"
    current_rental: Optional[CurrentRentalInfo] = None

    class Config:
        from_attributes = True
class PropertyDetail(Property):
    rentals: List[Rental] = []
    expenses: List[Expense] = []