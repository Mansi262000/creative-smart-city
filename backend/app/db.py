import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ---- Environment (defaults are fine for local/Codespaces) ----
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "smartcity")
DB_USER = os.getenv("DB_USER", "city")
DB_PASSWORD = os.getenv("DB_PASSWORD", "city")
ALLOW_DEMO_SEED = os.getenv("ALLOW_DEMO_SEED", "false").lower() == "true"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ---- SQLAlchemy base/session/engine ----
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_demo_user_if_enabled() -> None:
    """
    Creates tables and seeds demo roles/sensors/admin iff ALLOW_DEMO_SEED=true.
    NOTE: imports are inside the function to avoid circular imports:
      - models.py imports Base from this file
      - auth.py imports models
      - this file must not import models/auth at module import time
    """
    if not ALLOW_DEMO_SEED:
        # still ensure tables exist
        Base.metadata.create_all(bind=engine)
        return

    # Lazy imports to break circular dependency
    from . import models
    from .auth import get_password_hash

    # Create tables (prefer Alembic in production)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Roles
        roles = ["admin", "environment_officer", "utility_officer", "traffic_control", "viewer"]
        for r in roles:
            if not db.query(models.Role).filter_by(name=r).first():
                db.add(models.Role(name=r))
        db.commit()

        # Sensors (seed a few demo sensors)
        if db.query(models.Sensor).count() == 0:
            db.add_all(
                [
                    models.Sensor(
                        name="AQM-001", type="air_quality_pm25", location_lat=12.97, location_lng=77.59
                    ),
                    models.Sensor(
                        name="TRF-101", type="traffic_congestion", location_lat=12.98, location_lng=77.60
                    ),
                    models.Sensor(
                        name="WST-201", type="waste_level", location_lat=12.99, location_lng=77.61
                    ),
                    models.Sensor(
                        name="ENG-301", type="energy_usage", location_lat=13.00, location_lng=77.62
                    ),
                ]
            )
            db.commit()

        # Admin user
        admin_email = "admin@example.com"
        if not db.query(models.User).filter_by(email=admin_email).first():
            admin_role = db.query(models.Role).filter_by(name="admin").first()
            user = models.User(
                email=admin_email,
                password_hash=get_password_hash("admin123"),
                role_id=admin_role.id if admin_role else None,
            )
            db.add(user)
            db.commit()
    finally:
        db.close()
