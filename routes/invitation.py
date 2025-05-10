from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.invitation import Invitation
from models.job_offer import JobOffer
from models.user import User
from schemas import InvitationCreate, InvitationResponse
from routes.auth import get_current_user

router = APIRouter(prefix="/invitations", tags=["Invitations"])

@router.post("/", response_model=InvitationResponse)
def invite_candidate(
    invitation: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Sprawdzenie czy pracodawca
    if current_user.role != "employer":
        raise HTTPException(status_code=403, detail="Only employers can send invitations")

    # Czy oferta należy do tego pracodawcy
    offer = db.query(JobOffer).filter(JobOffer.id == invitation.offer_id).first()
    if not offer or offer.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only invite to your own offers")

    # Czy zaproszenie już istnieje
    existing = db.query(Invitation).filter(
        Invitation.offer_id == invitation.offer_id,
        Invitation.candidate_id == invitation.candidate_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Candidate already invited")

    new_inv = Invitation(
        offer_id=invitation.offer_id,
        candidate_id=invitation.candidate_id,
        message=invitation.message
    )
    db.add(new_inv)
    db.commit()
    db.refresh(new_inv)

    return new_inv

@router.get("/received", response_model=list[InvitationResponse])
def get_my_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can view invitations")

    invitations = (
        db.query(Invitation)
        .select_from(Invitation)
        .join(JobOffer, Invitation.offer_id == JobOffer.id)
        .join(User, JobOffer.employer_id == User.id)
        .filter(Invitation.candidate_id == current_user.id)
        .all()
    )

    return invitations
