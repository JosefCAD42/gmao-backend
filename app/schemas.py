from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import datetime

# 🔹 ENUMS

class UserRole(str, Enum):
    technician = "technician"
    manager = "manager"

class SensorStatus(str, Enum):
    available = "available"
    rented = "rented"
    returned = "returned"
    maintenance = "maintenance"

# 🔹 UTILISATEUR

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str  # sera hashé dans la base

class UserRead(UserBase):
    id: str
    class Config:
        orm_mode = True


# 🔹 CAPTEUR

class SensorBase(BaseModel):
    reference: str
    type: str
    subtype: str
    status: Optional[SensorStatus] = SensorStatus.available
    chantier: Optional[str] = None

class SensorCreate(SensorBase):
    pass

class SensorRead(SensorBase):
    id: str
    date_creation: datetime

    class Config:
        orm_mode = True


# 🔹 CHECKLIST & ITEMS

class ChecklistItemBase(BaseModel):
    label: str
    is_before: bool  # True = avant maintenance

class ChecklistItemCreate(ChecklistItemBase):
    pass

class ChecklistItemRead(ChecklistItemBase):
    id: str
    class Config:
        orm_mode = True

class ChecklistBase(BaseModel):
    type: str
    subtype: str

class ChecklistCreate(ChecklistBase):
    items: List[ChecklistItemCreate]

class ChecklistRead(ChecklistBase):
    id: str
    items: List[ChecklistItemRead]
    class Config:
        orm_mode = True


# 🔹 REPONSES DE CHECKLIST

class ChecklistResponseBase(BaseModel):
    sensor_id: str
    item_id: str
    is_checked: bool

class ChecklistResponseCreate(ChecklistResponseBase):
    user_id: str

class ChecklistResponseRead(ChecklistResponseBase):
    id: str
    date_checked: datetime
    user: UserRead
    class Config:
        orm_mode = True


# 🔹 MOUVEMENT CAPTEUR

class SensorMovementBase(BaseModel):
    sensor_id: str
    chantier: str
    date_depart: Optional[datetime]
    date_retour: Optional[datetime]
    commentaire: Optional[str] = None

class SensorMovementCreate(SensorMovementBase):
    pass

class SensorMovementRead(SensorMovementBase):
    id: str
    class Config:
        orm_mode = True

class SensorReturnRequest(BaseModel):
    sensor_id: str
    chantier: str
    date_retour: Optional[datetime] = None

class ChecklistItemReadSeparated(BaseModel):
    id: str
    label: str

class SensorReturnResponse(BaseModel):
    checklist_id: str
    before_maintenance: List[ChecklistItemReadSeparated]
    after_maintenance: List[ChecklistItemReadSeparated]

class ChecklistResponseCreate(BaseModel):
    sensor_id: str
    item_id: str
    user_id: str
    is_checked: bool

class ChecklistResponseBatch(BaseModel):
    responses: List[ChecklistResponseCreate]

class ChecklistResponseCreate(BaseModel):
    sensor_id: str
    item_id: str
    user_id: str
    is_checked: bool
    is_before: bool  # 🔹 Indique si c’est avant ou après maintenance

class ChecklistResponseRead(BaseModel):
    id: str
    sensor_id: str
    item_id: str
    user_id: str
    is_checked: bool
    is_before: bool
    date_checked: datetime

    class Config:
        orm_mode = True


class UserRole(str, Enum):
    technician = "technician"
    manager = "manager"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    registration_key: str

class UserRead(UserBase):
    id: str
    class Config:
        orm_mode = True

class SensorHistoryMovement(BaseModel):
    chantier: str
    date_depart: Optional[datetime]
    date_retour: Optional[datetime]
    commentaire: Optional[str]

    class Config:
        orm_mode = True

class ChecklistResponseItem(BaseModel):
    item_id: str
    label: str
    is_checked: bool
    is_before: bool
    user: UserRead
    date_checked: datetime

    class Config:
        orm_mode = True

class SensorHistoryResponse(BaseModel):
    sensor_id: str
    type: str
    subtype: str
    mouvements: List[SensorHistoryMovement]
    checklist_responses: Dict[str, List[ChecklistResponseItem]]  # {"avant": [], "apres": []}