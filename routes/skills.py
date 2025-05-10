from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.skill import Skill
from typing import List, Dict
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("/", response_class=JSONResponse)
def get_skills_grouped(db: Session = Depends(get_db)) -> Dict[str, List[Dict]]:
    """
    Zwraca wszystkie umiejętności pogrupowane według kategorii.
    """
    skills = db.query(Skill).all()
    grouped = {}

    for skill in skills:
        category = skill.category or "Inne"
        if category not in grouped:
            grouped[category] = []
        grouped[category].append({
            "id": skill.id,
            "name": skill.name
        })

    return grouped
