from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.models.model_role import Role
from app.models.model_user import User
from app.models.model_userrole import UserRole
from app.services.service_auth import create_access_token, get_current_user, hash_password, verify_password

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


class AuthUserData(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None
    roles: list[dict[str, str | int]]
    is_active: bool


class AuthResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    data: AuthUserData


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=6, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Email is not valid")
        return value


def get_role_names(user: User) -> list[str]:
    return [role.name for role in user.roles]


def user_data(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
            }
            for role in user.roles
        ],
        "is_active": user.is_active,
    }


def auth_response(message: str, user: User) -> dict:
    access_token = create_access_token(
        user.id,
        user.email,
        user.full_name,
        get_role_names(user),
    )

    return {
        "message": message,
        "access_token": access_token,
        "token_type": "bearer",
        "data": user_data(user),
    }


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
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

    role = db.query(Role).filter(Role.name == "user").first()
    if role is None:
        role = Role(name="user")
        db.add(role)
        db.flush()

    user = User(
        full_name=body.full_name,
        email=body.email,
        password=hash_password(body.password),
        phone=body.phone,
    )

    db.add(user)
    db.flush()

    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.add(user_role)
    db.commit()
    db.refresh(user)

    return auth_response("Register successfully", user)


@router.post("/login", response_model=AuthResponse)
def login_user(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email does not exist",
        )

    if not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return auth_response("Login successfully", user)


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "data": current_user,
    }
