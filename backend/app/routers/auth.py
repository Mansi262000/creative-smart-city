from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..auth import verify_password, create_access_token

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_access_token(sub=user.email)
    
    return {
        "access_token": token,
        "token_type": "bearer", 
        "expires_in": 3600,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.email,
            "first_name": "",
            "last_name": "",
            "department": "",
            "is_active": True,
            "role": None,
            "last_login": None,
            "created_at": "2025-09-16T12:00:00Z"
        }
    }
