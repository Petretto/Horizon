from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from models.user import User
from schemas import UserCreate, UserResponse, TokenResponse, RefreshTokenRequest
import schemas
from utils import hash_password
import jwt
import datetime
from passlib.context import CryptContext
from database import get_db
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS, REFRESH_TOKEN_EXPIRE_DAYS
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from uuid import uuid4
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

    

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Tworzy access token ważny przez ACCESS_TOKEN_EXPIRE_HOURS"""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    
    try:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except PyJWTError:
        raise HTTPException(status_code=500, detail="Token generation failed")

def create_refresh_token():
    """Tworzy refresh token ważny przez REFRESH_TOKEN_EXPIRE_DAYS"""
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    token = str(uuid4())  # Unikalny identyfikator jako refresh token
    return token, expire

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Pobiera aktualnego użytkownika na podstawie access tokena"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user    

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        company_name=user.company_name if user.role == "employer" else None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logowanie – zwraca access token i refresh token"""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email, "role": user.role})
    refresh_token, refresh_expiry = create_refresh_token()

    # Zapisujemy refresh token w bazie
    user.refresh_token = refresh_token
    user.refresh_expiry = refresh_expiry  # 🆕 Przechowujemy czas ważności
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Odświeża access token na podstawie refresh tokena"""
    user = db.query(User).filter(User.refresh_token == request.refresh_token).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # 🆕 Sprawdzenie, czy refresh token wygasł
    if user.refresh_expiry < datetime.datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired, please log in again")

    # Generujemy nowy access token i refresh token
    access_token = create_access_token({"sub": user.email, "role": user.role})
    new_refresh_token, new_refresh_expiry = create_refresh_token()

    # Aktualizujemy refresh token w bazie
    user.refresh_token = new_refresh_token
    user.refresh_expiry = new_refresh_expiry
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Wylogowanie – usuwa refresh token użytkownika"""
    user.refresh_token = None
    db.commit()
    return {"message": "Pomyślnie wylogowano"}

@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Pobiera profil zalogowanego użytkownika"""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pozwala użytkownikowi na aktualizację swojego profilu"""
    if update_data.email:
        # sprawdzamy, czy email już istnieje
        existing_user = db.query(User).filter(User.email == update_data.email).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email już istnieje")
        current_user.email = update_data.email
    if update_data.password:
        current_user.password = pwd_context.hash(update_data.password)

    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.delete("/me", response_model=dict)
def delete_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Usuwa konto użytkownika"""
    db.delete(current_user)
    db.commit()
    return {"message": "Użytkownik usunięty pomyślnie"}

