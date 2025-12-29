from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Expense(Base):

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("property.id")) 
    
    expense_title = Column(String(255), nullable=False) # Ex: "Conta de Luz Jan/25"
    category = Column(String(255), nullable=False) 
    amount = Column(Float, nullable=False) 
    pay_date = Column(Date, nullable=False) 
    
    description = Column(String(255), nullable=True) 
    created_at = Column(DateTime, default=func.now())

    property = relationship("Property", back_populates="expenses")