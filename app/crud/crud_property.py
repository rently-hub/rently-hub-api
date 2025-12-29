from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate
from app import models
class CRUDProperty(CRUDBase[Property, PropertyCreate, PropertyUpdate]):

    def get(self, db: Session, id: int) -> Optional[Property]:
        return (
            db.query(self.model)
            .filter(self.model.id == id)
            .options(
                joinedload(models.Property.rentals),
                joinedload(models.Property.expenses)
            )
            .first()
        )
    
    def create_with_owner(
        self, db: Session, *, obj_in: PropertyCreate, owner_id: int
    ) -> Property:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Property]:
        return (
            db.query(self.model)
            .filter(Property.owner_id == owner_id)
            .options(joinedload(models.Property.rentals))
            .offset(skip)
            .limit(limit)
            .all()
        )

property = CRUDProperty(Property)