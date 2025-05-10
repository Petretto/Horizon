from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.skill import Skill
from models.certification import Certification
from models.user import User
from schemas import SkillCreate, SkillResponse, CertificationCreate, CertificationResponse
from database import get_db
from routes.auth import get_current_user
from typing import List

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.post("/skills", response_model=SkillResponse)
def add_skill(skill: SkillCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_skill = Skill(**skill.dict(), user_id=current_user.id)
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.post("/certifications", response_model=CertificationResponse)
def add_cert(cert: CertificationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_cert = Certification(**cert.dict(), user_id=current_user.id)
    db.add(new_cert)
    db.commit()
    db.refresh(new_cert)
    return new_cert
