from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import Base

class UserSkill(Base):
    __tablename__ = "user_skills"
    __table_args__ = (
        UniqueConstraint('user_id', 'skill_id', name='unique_user_skill'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    level = Column(String, nullable=False)

    user = relationship("User", back_populates="skills")
    skill = relationship("Skill")
