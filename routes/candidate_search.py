from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.skill import Skill
from schemas import CandidateResponse
from typing import List

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.post("/search", response_model=List[CandidateResponse])
def search_candidates(skill_ids: List[int], db: Session = Depends(get_db)):
    if not skill_ids:
        raise HTTPException(status_code=400, detail="Musisz podać przynajmniej jedną umiejętność.")

    # Znajdź kandydatów, którzy mają przynajmniej jedną z wybranych umiejętności
    candidates = (
        db.query(User)
        .filter(User.role == "candidate")
        .join(User.skills)
        .filter(Skill.id.in_(skill_ids))
        .distinct()
        .all()
    )
    return candidates
