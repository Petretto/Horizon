from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.skill import Skill
import json

router = APIRouter(prefix="/skills", tags=["Skills Seed"])

@router.post("/seed")
def seed_skills(db: Session = Depends(get_db)):
    try:
        with open("skills_seed.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        for group in data:
            category = group.get("category")
            for skill_data in group.get("skills", []):
                name = skill_data.get("name")

                # Sprawdzenie, czy już istnieje
                exists = db.query(Skill).filter_by(name=name, category=category).first()
                if not exists:
                    new_skill = Skill(name=name, category=category)
                    db.add(new_skill)

        db.commit()
        return {"message": "Skills seeded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error seeding skills: {e}")
