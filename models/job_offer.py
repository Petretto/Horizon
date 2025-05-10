# models/job_offer.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class JobOffer(Base):
    __tablename__ = "job_offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    location = Column(String)
    company_name = Column(String)
    posted_at = Column(DateTime, default=datetime.utcnow)

    employer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    employer = relationship("User", backref="job_offers")

    required_skills = relationship("OfferSkill", back_populates="offer", cascade="all, delete-orphan")
