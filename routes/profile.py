from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.skill import Skill
from models.certification import Certification
from models.user import User
from models.user_skill import UserSkill
from schemas import SkillCreate, SkillResponse, CertificationCreate, CertificationResponse
from database import get_db
from routes.auth import get_current_user
from typing import List

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.post("/skills", response_model=SkillResponse)
def add_skill_to_profile(skill_data: SkillCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can add skills")

    existing = db.query(UserSkill).filter_by(user_id=current_user.id, skill_id=skill_data.skill_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Skill already added")

    new_user_skill = UserSkill(user_id=current_user.id, skill_id=skill_data.skill_id, level=skill_data.level)
    db.add(new_user_skill)
    db.commit()
    db.refresh(new_user_skill)
    return new_user_skill.skill  # ← zwracamy obiekt umiejętności (dla frontend)


@router.post("/certifications", response_model=CertificationResponse)
def add_cert(cert: CertificationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_cert = Certification(**cert.dict(), user_id=current_user.id)
    db.add(new_cert)
    db.commit()
    db.refresh(new_cert)
    return new_cert
