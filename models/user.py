from sqlalchemy import Column, Integer, String, DateTime, Enum
import datetime
from models.base import Base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum



class UserRole(PyEnum):
    candidate = "candidate"
    employer = "employer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String)
    role = Column(Enum(UserRole), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    company_name = Column(String, nullable=True)  # tylko dla pracodawcy 
    refresh_token = Column(String, nullable=True)
    refresh_expiry = Column(DateTime, nullable=True)  # 🆕 Dodajemy datę wygaśnięcia refresh_tokena
    
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="user", cascade="all, delete-orphan")
