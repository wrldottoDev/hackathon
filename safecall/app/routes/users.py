from __future__ import annotations

import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


def _generate_cr_number(db: Session) -> str:
    for _ in range(100):
        num = f"+5068{random.randint(100, 999)}{random.randint(1000, 9999)}"
        if not db.query(User).filter(User.assigned_simulated_number == num).first():
            return num
    raise RuntimeError("No se pudo generar un numero unico")


@router.post("/", response_model=UserOut, status_code=201)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email ya registrado")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        assigned_simulated_number=_generate_cr_number(db),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=list[UserOut])
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
