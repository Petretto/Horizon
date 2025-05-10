from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base
import datetime

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"))
    offer_id = Column(Integer, ForeignKey("job_offers.id"))
    applied_at = Column(DateTime, default=datetime.datetime.utcnow)

    candidate = relationship("User")
    offer = relationship("JobOffer")
