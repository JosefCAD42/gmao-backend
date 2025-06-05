from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from typing import List
from fastapi import Query
from datetime import date
from app.exports import generate_sensor_history_excel
from typing import Optional

router = APIRouter(prefix="/sensors", tags=["sensors"])

@router.post("/", response_model=schemas.SensorRead)
def create_sensor(sensor: schemas.SensorCreate, db: Session = Depends(get_db)):
    # user_id fictif pour tester
    return crud.create_sensor(db, sensor, user_id="1234")

from typing import List

@router.get("/", response_model=List[schemas.SensorRead])
def list_sensors(db: Session = Depends(get_db)):
    return crud.get_all_sensors(db)


@router.post("/sensor-return", response_model=schemas.SensorReturnResponse)
def sensor_return(
    return_data: schemas.SensorReturnRequest,
    db: Session = Depends(get_db)
):
    return crud.process_sensor_return(db, return_data)



@router.get("/{sensor_id}/history", response_model=schemas.SensorHistoryResponse)
def get_sensor_history(
    sensor_id: str,
    chantier: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    return crud.get_sensor_history(db, sensor_id, chantier, start_date, end_date)


@router.get("/{sensor_id}/history/export")
def export_sensor_history(
    sensor_id: str,
    format: Optional[str] = "excel",
    db: Session = Depends(get_db)
):
    sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Capteur introuvable")

    mouvements = db.query(models.SensorMovement).filter_by(sensor_id=sensor_id).all()
    responses = db.query(models.ChecklistResponse).filter_by(sensor_id=sensor_id).all()

    avant = [r for r in responses if r.is_before]
    apres = [r for r in responses if not r.is_before]

    if format == "pdf":
        return generate_sensor_history_pdf(sensor, mouvements, avant, apres)
    else:
        return generate_sensor_history_excel(sensor, mouvements, avant, apres)