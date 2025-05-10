from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class Invitation(Base):
    __tablename__ = "invitations"

    # id = Column(Integer, primary_key=True, index=True)
    # employer_id = Column(Integer, ForeignKey("users.id"))
    # candidate_id = Column(Integer, ForeignKey("users.id"))
    # message = Column(Text)
    # sent_at = Column(DateTime, default=datetime.utcnow)

    # employer = relationship("User", foreign_keys=[employer_id], backref="sent_invitations")
    # candidate = relationship("User", foreign_keys=[candidate_id], backref="received_invitations")


# - zmiany w modelu Invitation - nie działa
    id = Column(Integer, primary_key=True)
    offer_id = Column(Integer, ForeignKey("job_offers.id"))
    candidate_id = Column(Integer, ForeignKey("users.id"))
    sent_at = Column(DateTime, default=datetime.utcnow)
    message = Column(Text)

    offer = relationship("JobOffer")
    candidate = relationship("User")
