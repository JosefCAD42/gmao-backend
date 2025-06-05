from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())


# 🔹 Rôles des utilisateurs
class UserRole(str, enum.Enum):
    technician = "technician"
    manager = "manager"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    created_sensors = relationship("Sensor", back_populates="created_by_user")
    checklist_responses = relationship("ChecklistResponse", back_populates="user")


# 🔹 Statut du capteur
class SensorStatus(str, enum.Enum):
    available = "available"
    rented = "rented"
    returned = "returned"
    maintenance = "maintenance"


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(String, primary_key=True, default=generate_uuid)
    reference = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    subtype = Column(String, nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(SensorStatus), default=SensorStatus.available)
    chantier = Column(String, nullable=True)

    created_by = Column(String, ForeignKey("users.id"))
    created_by_user = relationship("User", back_populates="created_sensors")

    checklist_responses = relationship("ChecklistResponse", back_populates="sensor")
    movements = relationship("SensorMovement", back_populates="sensor")


# 🔹 Checklist pour un type + sous-type de capteur
class Checklist(Base):
    __tablename__ = "checklists"

    id = Column(String, primary_key=True, default=generate_uuid)
    type = Column(String, nullable=False)
    subtype = Column(String, nullable=False)

    items = relationship("ChecklistItem", back_populates="checklist")


# 🔹 Éléments de checklist
class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    checklist_id = Column(String, ForeignKey("checklists.id"))
    label = Column(String, nullable=False)
    is_before = Column(Boolean, default=True)  # True = avant maintenance, False = après

    checklist = relationship("Checklist", back_populates="items")


# 🔹 Réponses aux checklists remplies par les techniciens
class ChecklistResponse(Base):
    __tablename__ = "checklist_responses"

    id = Column(String, primary_key=True, default=generate_uuid)
    sensor_id = Column(String, ForeignKey("sensors.id"))
    user_id = Column(String, ForeignKey("users.id"))
    item_id = Column(String, ForeignKey("checklist_items.id"))
    is_checked = Column(Boolean, default=False)
    date_checked = Column(DateTime, default=datetime.utcnow)

    sensor = relationship("Sensor", back_populates="checklist_responses")
    user = relationship("User", back_populates="checklist_responses")
    item = relationship("ChecklistItem")


# 🔹 Historique des mouvements de capteurs (chantier, dates)
class SensorMovement(Base):
    __tablename__ = "sensor_movements"

    id = Column(String, primary_key=True, default=generate_uuid)
    sensor_id = Column(String, ForeignKey("sensors.id"))
    chantier = Column(String, nullable=False)
    date_depart = Column(DateTime, nullable=True)
    date_retour = Column(DateTime, nullable=True)
    commentaire = Column(Text, nullable=True)

    sensor = relationship("Sensor", back_populates="movements")
