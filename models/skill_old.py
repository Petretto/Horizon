from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    level = Column(String, nullable=False)  # np. "początkujący", "średniozaawansowany", "zaawansowany"
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="skills")
