from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import crud
from app.schemas.rental import RentalCreate
from app.models.rental import Rental

class RentalService:
    @staticmethod
    def create_rental(db: Session, rental_in: RentalCreate) -> Rental:
        property_obj = crud.property.get(db, id=rental_in.property_id)
    
        if not property_obj:
            raise HTTPException(status_code=404, detail="Propriedade não encontrada")

        # 2. Calcular dias
        delta = rental_in.end_date - rental_in.start_date
        days = delta.days
        if days < 1: 
            days = 1

        # 3. Calcular preço
        base_price = days * property_obj.price_per_day
        
        #(Dias * Diária) - Limpeza
        final_price = base_price - property_obj.cleaning_fee

        if final_price < 0:
            final_price = 0.0

        rental_data = rental_in.model_dump()
        rental_data["total_price"] = final_price

        db_obj = Rental(**rental_data)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj

rental_service = RentalService()