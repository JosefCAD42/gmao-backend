from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, auth
from app.database import get_db
from datetime import timedelta
from app import schemas, crud, auth
import os
from dotenv import load_dotenv


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Identifiants incorrects")

    token = auth.create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def get_me(user: models.User = Depends(auth.get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role
    }





load_dotenv()
MANAGER_KEY = os.getenv("MANAGER_KEY")
TECHNICIAN_KEY = os.getenv("TECHNICIAN_KEY")

@router.post("/register", response_model=schemas.UserRead)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Vérifier la clé
    if user.registration_key == MANAGER_KEY:
        role = "manager"
    elif user.registration_key == TECHNICIAN_KEY:
        role = "technician"
    else:
        raise HTTPException(status_code=403, detail="Clé d'inscription invalide")

    existing = db.query(models.User).filter_by(email=user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    return crud.create_user(db, user, role)