# models/skill.py
from sqlalchemy import Column, Integer, String
from models.base import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)  # np. IT, Produkcja, Języki, Biznes

