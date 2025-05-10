from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, JobOffer, Skill

router = APIRouter(prefix="/match", tags=["Matching"])

@router.get("/offers/{offer_id}/candidates")
def find_best_candidates(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(JobOffer).filter(JobOffer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    required_skills = {skill.id for skill in offer.required_skills}
    candidates = db.query(User).filter(User.role == "candidate").all()

    ranked_candidates = []

    for candidate in candidates:
        candidate_skill_ids = {skill.id for skill in candidate.skills}
        matched_skills = required_skills.intersection(candidate_skill_ids)
        score = len(matched_skills)  # Prosty system punktacji: 1 punkt za dopasowaną umiejętność

        ranked_candidates.append({
            "id": candidate.id,
            "email": candidate.email,
            "score": score,
            "matched_skills": list(matched_skills)
        })

    # Sortuj kandydatów malejąco po score
    ranked_candidates.sort(key=lambda x: x["score"], reverse=True)

    return ranked_candidates
