from sqlalchemy import Column, Integer, String, Boolean
from app.db.base_class import Base  
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    full_name = Column(String(255))
    properties = relationship("Property", back_populates="owner")