from datetime import date
from typing import List, Any
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app import models

from app import crud
from app.schemas.property import Property as PropertySchema

class PropertyService:
    
    def _calculate_status(self, property_obj) -> dict:
        """
        Método privado que pega um objeto do banco e adiciona 
        os campos calculados (status, current_rental).
        """
        property_data = jsonable_encoder(property_obj)
        
        today = date.today()
        active_rental = None

        if property_obj.rentals:
            for rental in property_obj.rentals:
                if rental.start_date <= today <= rental.end_date and rental.status == "active":
                    active_rental = rental
                    break
        
        if active_rental:
            property_data["status"] = "Ocupada"
            delta = active_rental.end_date - active_rental.start_date
            days = delta.days
            
            property_data["current_rental"] = {
                "rental_id": active_rental.id,
                "start_date": active_rental.start_date,
                "end_date": active_rental.end_date,
                "total_days": max(days, 1),
                "total_price": active_rental.total_price,
                "guest_name": "Cliente" 
            }
        else:
            property_data["status"] = "Disponível"
            property_data["current_rental"] = None
            
        return property_data

    def get_property_details(self, db: Session, id: int) -> dict:
        """Retorna UMA propriedade com status calculado"""
        property_obj = crud.property.get(db=db, id=id)
        if not property_obj:
            return None
        
        return self._calculate_status(property_obj)

    def get_owner_properties(self, db: Session, owner_id: int, skip: int=0, limit: int=100) -> List[dict]:
        """Retorna TODAS as propriedades do dono com status calculado"""
        properties = crud.property.get_multi_by_owner(db=db, owner_id=owner_id, skip=skip, limit=limit)

        return [self._calculate_status(prop) for prop in properties]
    
  

property_service = PropertyService()