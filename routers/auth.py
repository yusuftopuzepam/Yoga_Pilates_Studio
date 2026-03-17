import email

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database.db_connection import get_db
from core.database.tables import User, UserRole
from core.security import (
    verify_password,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from pydantic_models.auth_model import TokenResponse, LoginRequest, UserCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email zaten kayıtlı")

    hashed_password = get_password_hash(user_in.password)

    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Kullanıcı oluşturuldu"}


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Kullanici adi veya sifre hatali")

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role.value,
        }
    )
    return TokenResponse(access_token=access_token)


@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value,
    }
