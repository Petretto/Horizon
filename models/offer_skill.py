# models/offer_skill.py
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from models.base import Base

class OfferSkill(Base):
    __tablename__ = "offer_skills"

    id = Column(Integer, primary_key=True)
    offer_id = Column(Integer, ForeignKey("job_offers.id", ondelete="CASCADE"))
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"))
    level = Column(String, nullable=False)  # 'początkujący', 'średniozaawansowany', 'zaawansowany'

    offer = relationship("JobOffer", back_populates="required_skills")
    skill = relationship("Skill")  # bezpośrednio po nazwie modelu, by uniknąć importu
