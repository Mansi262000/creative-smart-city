from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from .. import models, schemas
from ..auth import get_current_user, require_roles

router = APIRouter()

@router.get("/", response_model=List[schemas.SensorOut])
def list_sensors(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Sensor).all()

@router.post("/", response_model=schemas.SensorOut)
def create_sensor(payload: schemas.SensorCreate, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    s = models.Sensor(
        name=payload.name,
        type=payload.type,
        location_lat=payload.location_lat,
        location_lng=payload.location_lng,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s
