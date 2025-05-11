from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes.auth import router as auth_router
from routes import job_offer, application, profile, invitation
from routes.skills_seed import router as seed_router
from routes.skills import router as skills_router
from routes.candidate_search import router as candidate_router
from routes.match import router as match_router
from database import engine, Base
import os

Base.metadata.create_all(bind=engine)
app = FastAPI()

# ⚙️ CORS — dopuszczamy dostęp z lokalnego frontendu
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# 🧩 Routers
app.include_router(auth_router)
app.include_router(job_offer.router)
app.include_router(application.router)
app.include_router(profile.router)
app.include_router(seed_router)
app.include_router(skills_router)
app.include_router(candidate_router)
app.include_router(match_router)
app.include_router(invitation.router)

# 📁 Serwowanie statycznych plików
frontend_dir = os.path.join(os.path.dirname(__file__), "Frontend")  # zakładamy, że pliki są w folderze "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# 🏠 Główna strona — index.html
@app.get("/")
def root():
    # return FileResponse(os.path.join(frontend_dir, "index.html"))
    return FileResponse(os.path.join(frontend_dir, "index.html"))
