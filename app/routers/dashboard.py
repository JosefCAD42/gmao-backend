from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app import models

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/")
def get_dashboard_data(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    start_of_month = now.replace(day=1)

    # 🔄 Capteurs retournés ce mois
    capteurs_retour_mois = db.query(models.SensorMovement)\
        .filter(models.SensorMovement.date_retour >= start_of_month)\
        .count()

    # ✅ Taux de conformité checklist (taux de cases cochées)
    total = db.query(models.ChecklistResponse).count()
    cochées = db.query(models.ChecklistResponse).filter(models.ChecklistResponse.is_checked == True).count()
    taux_checklist = round((cochées / total * 100), 1) if total > 0 else 0.0

    # 📆 Temps moyen entre retours de capteurs
    capteurs = db.query(models.Sensor).all()
    deltas = []
    for sensor in capteurs:
        mouvements = db.query(models.SensorMovement)\
            .filter(models.SensorMovement.sensor_id == sensor.id)\
            .order_by(models.SensorMovement.date_retour.asc()).all()
        if len(mouvements) > 1:
            for i in range(1, len(mouvements)):
                if mouvements[i - 1].date_retour and mouvements[i].date_retour:
                    delta = (mouvements[i].date_retour - mouvements[i - 1].date_retour).days
                    deltas.append(delta)
    temps_moyen = round(sum(deltas) / len(deltas), 1) if deltas else 0.0

    # 🔧 Capteurs les plus souvent maintenus
    top_maintenus = db.query(
        models.SensorMovement.sensor_id,
        func.count(models.SensorMovement.id).label("nb")
    ).group_by(models.SensorMovement.sensor_id).order_by(func.count(models.SensorMovement.id).desc()).limit(5).all()

    plus_maintenus = [{"capteur_id": r.sensor_id, "nb_interventions": r.nb} for r in top_maintenus]

    # 🧑 Top techniciens
    top_techs = db.query(
        models.User.name,
        func.count(models.ChecklistResponse.id).label("interventions")
    ).join(models.ChecklistResponse.user)\
     .group_by(models.User.name)\
     .order_by(func.count(models.ChecklistResponse.id).desc())\
     .limit(5).all()

    top_techniciens = [{"nom": r.name, "interventions": r.interventions} for r in top_techs]

    return {
        "capteurs_retournes_ce_mois": capteurs_retour_mois,
        "taux_checklist_remplie": taux_checklist,
        "temps_moyen_entre_retours": temps_moyen,
        "plus_maintenus": plus_maintenus,
        "top_techniciens": top_techniciens
    }