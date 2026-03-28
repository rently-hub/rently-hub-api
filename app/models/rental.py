from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("property.id"), nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    guest_count = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    status = Column(String(50), default="active")  # active, cancelled, completed
    platform_source = Column(String(50), default="Direto") # Airbnb, Booking, etc.
    
    external_uid = Column(String(255), unique=True, index=True, nullable=True)
    is_external = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    property = relationship("Property", back_populates="rentals")
