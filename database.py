from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models.user import User
from models.application import Application
from models.job_offer import JobOffer
from models.base import Base
from models.skill import Skill
from models.certification import Certification
from models.invitation import Invitation
from models.offer_skill import OfferSkill

  

DATABASE_URL = "postgresql://job_admin:AliCzek2019!@localhost/wip_platform"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()