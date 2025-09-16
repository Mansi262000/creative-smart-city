from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta, timezone
from ..db import get_db
from .. import models, schemas
from ..auth import get_current_user
from ..services import rules, notifier

router = APIRouter()

@router.post("/ingest", response_model=schemas.MetricOut)
def ingest_metric(payload: schemas.MetricIn, db: Session = Depends(get_db)):
    m = models.Metric(
        sensor_id=payload.sensor_id,
        metric_type=payload.type,
        value=payload.value,
        ts=payload.ts or datetime.now(timezone.utc),
    )
    db.add(m)
    db.commit()
    db.refresh(m)

    res = rules.evaluate(m.metric_type, m.value)
    if res:
        severity, message = res
        alert = models.Alert(sensor_id=m.sensor_id, metric_type=m.metric_type, severity=severity, message=message)
        db.add(alert)
        db.commit()
        notifier.notify(severity, message)

    return m

@router.get("/summary", response_model=List[schemas.SummaryPoint])
def summary(hours: int = 1, db: Session = Depends(get_db), user=Depends(get_current_user)):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    q = (
        db.query(
            models.Metric.metric_type,
            func.count(models.Metric.id),
            func.avg(models.Metric.value),
            func.min(models.Metric.value),
            func.max(models.Metric.value),
        )
        .filter(models.Metric.ts >= since)
        .group_by(models.Metric.metric_type)
    )
    results = q.all()
    return [
        schemas.SummaryPoint(
            metric_type=r[0], count=int(r[1]), avg=float(r[2] or 0), min=float(r[3] or 0), max=float(r[4] or 0)
        ) for r in results
    ]
