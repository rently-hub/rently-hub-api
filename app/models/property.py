from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Property(Base):

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False) 
    description = Column(Text, nullable=True)
    address = Column(String(255), nullable=True)
    photo_url = Column(String(500), nullable=True) 
    
    price_per_day = Column(Float, nullable=False)
    cleaning_fee = Column(Float, default=0.0) 
    max_guests = Column(Integer, default=1)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="properties")

    rentals = relationship("Rental", back_populates="property", cascade="all, delete-orphan")

    expenses = relationship("Expense", back_populates="property", cascade="all, delete-orphan")