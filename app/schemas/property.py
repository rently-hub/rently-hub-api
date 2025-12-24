from typing import Optional
from pydantic import BaseModel

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

class Property(PropertyBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True