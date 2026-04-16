from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import create_access_token, hash_password, verify_and_update_password
from ..models.user import User
from ..schemas.user import UserCreate


def register_user(db: Session, data: UserCreate) -> User:
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )
    user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> tuple[str, User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    verified, updated_hash = verify_and_update_password(password, user.hashed_password)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if updated_hash:
        user.hashed_password = updated_hash
        db.add(user)
        db.commit()

    token = create_access_token({"sub": str(user.id)})
    return token, user
