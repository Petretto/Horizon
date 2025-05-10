from sqlalchemy import Column, Integer, String, DateTime
import datetime
from models.base import Base
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="candidate")  # "candidate" lub "employer"
    refresh_token = Column(String, nullable=True)
    refresh_expiry = Column(DateTime, nullable=True)  # 🆕 Dodajemy datę wygaśnięcia refresh_tokena
    
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="user", cascade="all, delete-orphan")
