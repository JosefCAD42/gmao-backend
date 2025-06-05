from sqlalchemy.orm import Session
from app import models, schemas, auth
from typing import Optional

def create_sensor(db: Session, sensor: schemas.SensorCreate, user_id: str):
    db_sensor = models.Sensor(**sensor.dict(), created_by=user_id)
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def get_all_sensors(db: Session):
    return db.query(models.Sensor).all()


def create_checklist(db: Session, checklist_data: schemas.ChecklistCreate):
    checklist = models.Checklist(
        type=checklist_data.type,
        subtype=checklist_data.subtype
    )
    db.add(checklist)
    db.flush()  # pour obtenir l'ID sans commit complet

    for item in checklist_data.items:
        checklist_item = models.ChecklistItem(
            checklist_id=checklist.id,
            label=item.label,
            is_before=item.is_before
        )
        db.add(checklist_item)

    db.commit()
    db.refresh(checklist)
    return checklist

def process_sensor_return(db: Session, return_data: schemas.SensorReturnRequest):
    # 1. Récupérer le capteur
    sensor = db.query(models.Sensor).filter(models.Sensor.id == return_data.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Capteur non trouvé")

    # 2. Enregistrer le retour chantier
    movement = models.SensorMovement(
        sensor_id=sensor.id,
        chantier=return_data.chantier,
        date_retour=return_data.date_retour or datetime.utcnow()
    )
    db.add(movement)

    # 3. Récupérer la checklist associée au type/sous-type
    checklist = db.query(models.Checklist).filter_by(
        type=sensor.type,
        subtype=sensor.subtype
    ).first()

    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist introuvable pour ce type de capteur")

    db.commit()

    # 4. Séparer les items
    before_items = []
    after_items = []

    for item in checklist.items:
        dto = schemas.ChecklistItemReadSeparated(id=item.id, label=item.label)
        if item.is_before:
            before_items.append(dto)
        else:
            after_items.append(dto)

    return schemas.SensorReturnResponse(
        checklist_id=checklist.id,
        before_maintenance=before_items,
        after_maintenance=after_items
    )

def create_checklist_responses(db: Session, data: schemas.ChecklistResponseBatch):
    for item in data.responses:
        response = models.ChecklistResponse(
            sensor_id=item.sensor_id,
            item_id=item.item_id,
            user_id=item.user_id,
            is_checked=item.is_checked,
            is_before=item.is_before
        )
        db.add(response)
    db.commit()
    return {"message": "Checklist enregistrée avec succès"}

def create_user(db: Session, user_data: schemas.UserCreate, role: str):
    hashed_password = auth.get_password_hash(user_data.password)
    db_user = models.User(
        name=user_data.name,
        email=user_data.email,
        role=role,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_sensor_history(
    db: Session,
    sensor_id: str,
    chantier: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Capteur introuvable")

    # 🔍 Mouvements filtrés
    mouvements_query = db.query(models.SensorMovement).filter_by(sensor_id=sensor_id)
    if chantier:
        mouvements_query = mouvements_query.filter(models.SensorMovement.chantier == chantier)
    if start_date:
        mouvements_query = mouvements_query.filter(models.SensorMovement.date_retour >= start_date)
    if end_date:
        mouvements_query = mouvements_query.filter(models.SensorMovement.date_retour <= end_date)
    mouvements = mouvements_query.all()

    # 🔍 Réponses checklist filtrées
    responses_query = db.query(models.ChecklistResponse).filter_by(sensor_id=sensor_id)
    if start_date:
        responses_query = responses_query.filter(models.ChecklistResponse.date_checked >= start_date)
    if end_date:
        responses_query = responses_query.filter(models.ChecklistResponse.date_checked <= end_date)
    responses = responses_query.all()

    avant, apres = [], []
    for resp in responses:
        dto = schemas.ChecklistResponseItem(
            item_id=resp.item_id,
            label=resp.item.label,
            is_checked=resp.is_checked,
            is_before=resp.is_before,
            user=resp.user,
            date_checked=resp.date_checked
        )
        if resp.is_before:
            avant.append(dto)
        else:
            apres.append(dto)

    return schemas.SensorHistoryResponse(
        sensor_id=sensor.id,
        type=sensor.type,
        subtype=sensor.subtype,
        mouvements=mouvements,
        checklist_responses={"avant": avant, "apres": apres}
    )