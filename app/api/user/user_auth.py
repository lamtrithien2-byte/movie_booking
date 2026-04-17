from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.models.model_user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str
    password: str = Field(min_length=6, max_length=255)
    phone: str | None = Field(default=None, max_length=20)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Full name is required")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Email is not valid")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if value and not value.replace("+", "").isdigit():
            raise ValueError("Phone must contain only numbers")
        return value or None


class RegisterUserData(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None
    role: str
    is_active: bool


class RegisterResponse(BaseModel):
    message: str
    data: RegisterUserData


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse)
def register_user(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    if body.phone and db.query(User).filter(User.phone == body.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already exists",
        )

    user = User(
        full_name=body.full_name,
        email=body.email,
        password=sha256(body.password.encode()).hexdigest(),
        phone=body.phone,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Register successfully",
        "data": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_active": user.is_active,
        },
    }
