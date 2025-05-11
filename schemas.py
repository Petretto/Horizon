from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# -------------------- UŻYTKOWNICY --------------------
class UserRole(str, Enum):
    candidate = "candidate"
    employer = "employer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# -------------------- SKILLS --------------------

class SkillCreate(BaseModel):
    skill_id: int
    level: str

class SkillResponse(SkillCreate):
    id: int
    name: str
    category: Optional[str] = None

    class Config:
        orm_mode = True

# -------------------- CERTYFIKATY --------------------

class CertificationCreate(BaseModel):
    title: str
    issuer: str
    year: Optional[int] = None

class CertificationResponse(CertificationCreate):
    id: int
    class Config:
        orm_mode = True

# -------------------- UŻYTKOWNIK - ODPOWIEDŹ --------------------

class UserSkillResponse(BaseModel):
    skill: SkillResponse
    level: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    skills: List[SkillResponse] = []
    certifications: List[CertificationResponse] = []

    class Config:
        orm_mode = True

class CandidateResponse(BaseModel):
    id: int
    email: str
    skills: List[SkillResponse] = []

    class Config:
        from_attributes = True

# -------------------- JOB OFFERS --------------------

class OffersSkillCreate(BaseModel):
    skill_id: int
    level: str  # 'początkujący', 'średniozaawansowany', 'zaawansowany'

class OfferSkillSkill(BaseModel):
    name: str

    class Config:
        orm_mode = True

class OfferSkillResponse(BaseModel):
    # skill_id: int
    # level: str
    # skill: OfferSkillSkill  # Zagnieżdżony obiekt
    skill: SkillResponse
    level: str

    class Config:
        orm_mode = True


class JobOfferCreate(BaseModel):
    title: str
    description: str
    location: str
    company_name: str
    skills: List[OffersSkillCreate]

class JobOfferShortResponse(BaseModel):
    id: int
    title: str
    company_name: str

    class Config:
        from_attributes = True

class JobOfferResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    company_name: str
    posted_at: datetime
    employer_id: int
    required_skills: List[OfferSkillResponse]

    class Config:
        orm_mode = True

# -------------------- APLIKACJE --------------------

class ApplicationCreate(BaseModel):
    offer_id: int

class ApplicationResponse(BaseModel):
    id: int
    offer_id: int
    candidate_id: int
    applied_at: datetime

    class Config:
        orm_mode = True

class ApplicationWithDetails(BaseModel):
    id: int
    offer: JobOfferResponse
    candidate: UserResponse
    applied_at: datetime

    class Config:
        orm_mode = True

# Zwracanie aplikacji kandydata z podstawowymi danymi o ofercie
class ApplicationOut(BaseModel):
    id: int
    applied_at: datetime
    status: Optional[str] = "Aktywna"  # Możliwość rozszerzenia w przyszłości
    offer: JobOfferShortResponse

    class Config:
        orm_mode = True


# -------------------- ZAPROSZENIA --------------------

class InvitationCreate(BaseModel):
    candidate_id: int
    offer_id: int
    message: str

class InvitationResponse(BaseModel):
    id: int
    candidate_id: int
    message: str
    sent_at: datetime
    offer: JobOfferShortResponse

    class Config:
        from_attributes = True
