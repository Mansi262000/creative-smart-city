from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import uuid
from ..db import get_db
from ..auth import get_current_user, require_roles
from .. import models, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.AlertOut])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get alerts with basic filtering and pagination"""
    
    query = db.query(models.Alert)
    alerts = query.offset(skip).limit(limit).all()
    return alerts

@router.post("/", response_model=schemas.AlertOut)
async def create_alert(
    alert: schemas.AlertCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new alert"""
    
    # Generate unique alert ID
    alert_id = f"ALERT-{alert.metric_type.upper()}-{uuid.uuid4().hex[:8].upper()}"
    
    # Get sensor information
    sensor = db.query(models.Sensor).get(alert.sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Calculate priority
    priority_map = {
        schemas.SeverityLevel.LOW: 1,
        schemas.SeverityLevel.MEDIUM: 2,
        schemas.SeverityLevel.HIGH: 3,
        schemas.SeverityLevel.CRITICAL: 4
    }
    priority = priority_map.get(alert.severity, 1)
    
    db_alert = models.Alert(
        alert_id=alert_id,
        sensor_id=alert.sensor_id,
        metric_type=alert.metric_type,
        severity=alert.severity,
        title=alert.title,
        message=alert.message,
        trigger_value=alert.trigger_value,
        threshold_value=alert.threshold_value,
        priority=priority,
        tags=[alert.metric_type]
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@router.get("/{alert_id}", response_model=schemas.AlertOut)
async def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific alert"""
    
    alert = db.query(models.Alert).filter(models.Alert.alert_id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert
