from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import sensors
from app.routers import checklists
from app.routers import users
from app.routers import dashboard
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplace "*" par l'URL exacte de ton frontend si tu veux plus de sécurité
    allow_credentials=True,
    allow_methods=["*"],  # ⬅️ très important pour autoriser les OPTIONS, POST, etc.
    allow_headers=["*"],  # ⬅️ permet les headers comme Authorization
)
# 👇 Crée toutes les tables à partir des modèles
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "GMAO backend connecté ✅"}

app.include_router(sensors.router)

app.include_router(checklists.router)

app.include_router(users.router)

app.include_router(dashboard.router)