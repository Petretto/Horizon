from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.application import Application
from models.job_offer import JobOffer
from models.user import User
from schemas import ApplicationCreate, ApplicationResponse
from routes.auth import get_current_user
from typing import List
from sqlalchemy.orm import joinedload
from schemas import ApplicationWithDetails, ApplicationOut

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/", response_model=ApplicationResponse)
def apply_to_offer(application: ApplicationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can apply")

    offer = db.query(JobOffer).filter(JobOffer.id == application.offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    # Sprawdź, czy już aplikowano
    existing = db.query(Application).filter_by(candidate_id=current_user.id, offer_id=application.offer_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied")

    new_application = Application(candidate_id=current_user.id, offer_id=application.offer_id)
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application

@router.get("/my-offers", response_model=List[ApplicationWithDetails])
def get_applications_for_my_offers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "employer":
        raise HTTPException(status_code=403, detail="Only employers can view this")

    applications = db.query(Application)\
        .join(JobOffer)\
        .options(joinedload(Application.candidate), joinedload(Application.offer))\
        .filter(JobOffer.employer_id == current_user.id)\
        .all()

    return applications

# ✅ Zwracanie aplikacji złożonych przez aktualnie zalogowanego kandydata
@router.get("/my", response_model=List[ApplicationOut])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 🔐 Tylko kandydaci mają dostęp do tej trasy
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can view their applications")

    # Pobranie aplikacji użytkownika z dołączoną ofertą (join)
    applications = (
        db.query(Application)
        .options(joinedload(Application.offer))
        .filter(Application.candidate_id == current_user.id)
        .all()
    )

    return applications
