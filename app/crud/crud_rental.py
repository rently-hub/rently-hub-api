from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.rental import Rental
from app.schemas.rental import RentalCreate, RentalUpdate


class CRUDRental(CRUDBase[Rental, RentalCreate, RentalUpdate]):

    def get_by_property(
            self, db: Session, *, property_id: int, skip: int = 0, limit: int = 100
    ) -> List[Rental]:
        return (
            db.query(Rental)
            .filter(Rental.property_id == property_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
rental = CRUDRental(Rental)