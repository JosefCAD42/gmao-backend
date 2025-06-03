from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/checklists",
    tags=["checklists"]
)

@router.post("/", response_model=schemas.ChecklistRead)
def create_checklist(checklist: schemas.ChecklistCreate, db: Session = Depends(get_db)):
    # 🔒 plus tard : vérifier que l'utilisateur est un manager
    return crud.create_checklist(db, checklist)


router = APIRouter(
    prefix="/checklists",
    tags=["checklists"]
)

@router.post("/responses")
def submit_checklist_responses(
    data: schemas.ChecklistResponseBatch,
    db: Session = Depends(get_db)
):
    return crud.create_checklist_responses(db, data)