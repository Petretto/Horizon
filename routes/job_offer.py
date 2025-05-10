from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.job_offer import JobOffer 
from models.user import User
from schemas import JobOfferCreate, JobOfferResponse, OfferSkillResponse
from routes.auth import get_current_user
from typing import List
from fastapi import HTTPException
from models.skill import Skill
from models.offer_skill import OfferSkill
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/offers", tags=["Job Offers"])

@router.post("/", response_model=JobOfferResponse)
def create_job_offer(
    offer: JobOfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "employer":
        raise HTTPException(status_code=403, detail="Only employers can create job offers")

    new_offer = JobOffer(
        title=offer.title,
        description=offer.description,
        location=offer.location,
        company_name=offer.company_name,
        employer_id=current_user.id
    )

    for skill_data in offer.skills:
        skill = db.query(Skill).filter(Skill.id == skill_data.skill_id).first()
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill with id {skill_data.skill_id} not found")

        offer_skill = OfferSkill(
            skill=skill,
            level=skill_data.level,
            offer=new_offer
        )
        new_offer.required_skills.append(offer_skill)

    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)

    # ✳️ Ręczna serializacja, by dołączyć `name` z relacji `skill`
    return {
        "id": new_offer.id,
        "title": new_offer.title,
        "description": new_offer.description,
        "location": new_offer.location,
        "company_name": new_offer.company_name,
        "posted_at": new_offer.posted_at,
        "employer_id": new_offer.employer_id,
        "required_skills": [
            {
                "skill_id": rs.skill_id,
                "level": rs.level,
                "name": rs.skill.name if rs.skill else ""
            } for rs in new_offer.required_skills
        ]
    }

@router.get("/", response_model=List[JobOfferResponse])
def list_job_offers(db: Session = Depends(get_db)):
    return db.query(JobOffer).all()

@router.put("/{offer_id}", response_model=JobOfferResponse)
def update_job_offer(offer_id: int, offer_data: JobOfferCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    offer = db.query(JobOffer).filter(JobOffer.id == offer_id).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this offer")

    offer.title = offer_data.title
    offer.description = offer_data.description
    offer.location = offer_data.location
    offer.company_name = offer_data.company_name

    # 🧹 Usuń poprzednie wymagane umiejętności
    offer.required_skills.clear()
    db.flush()

    # ➕ Dodaj nowe wymagane umiejętności
    for skill_data in offer_data.skills:
        skill = db.query(Skill).filter(Skill.id == skill_data.skill_id).first()
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill with id {skill_data.skill_id} not found")

        offer_skill = OfferSkill(
            skill=skill,
            level=skill_data.level,
            offer=offer
        )
        offer.required_skills.append(offer_skill)

    db.commit()
    db.refresh(offer)

    # return {
    #     "id": offer.id,
    #     "title": offer.title,
    #     "description": offer.description,
    #     "location": offer.location,
    #     "company_name": offer.company_name,
    #     "posted_at": offer.posted_at,
    #     "employer_id": offer.employer_id,
    #     "required_skills": [
    #         {
    #             "skill_id": rs.skill_id,
    #             "level": rs.level,
    #             "name": rs.skill.name if rs.skill else ""
    #         } for rs in offer.required_skills
    #     ]
    # }
    return offer


@router.delete("/{offer_id}")
def delete_job_offer(offer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    offer = db.query(JobOffer).filter(JobOffer.id == offer_id).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this offer")

    db.delete(offer)
    db.commit()
    return {"message": "Offer deleted"}

@router.get("/{offer_id}/candidates")
def find_matching_candidates(offer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    offer = db.query(JobOffer).filter(JobOffer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    required_skills = [skill.name.lower() for skill in offer.required_skills]

    candidates = db.query(User).filter(User.role == "candidate").all()
    matches = []

    for candidate in candidates:
        candidate_skills = [skill.name.lower() for skill in candidate.skills]
        match_score = len(set(required_skills) & set(candidate_skills))
        if match_score > 0:
            matches.append({
                "candidate_id": candidate.id,
                "email": candidate.email,
                "match_score": match_score,
                "skills": candidate_skills
            })

    # Sortuj od najlepiej dopasowanych
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches
