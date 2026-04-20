import base64
import hmac
import json
import os
import time
from collections.abc import Callable
from hashlib import sha256

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.models.model_user import User

SECRET_KEY = os.getenv("SECRET_KEY", "simple-secret-key")
ACCESS_TOKEN_EXPIRE_SECONDS = 3600
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    return hmac.compare_digest(hash_password(password), hashed_password)


def encode_base64_url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def decode_base64_url(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(user_id: int, email: str, full_name: str, roles: list[str]) -> str:
    header = {
        "alg": "HS256",
        "typ": "JWT",
    }
    payload = {
        "sub": str(user_id),
        "email": email,
        "full_name": full_name,
        "roles": roles,
        "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS,
    }
    header_base64 = encode_base64_url(json.dumps(header, separators=(",", ":")).encode())
    payload_base64 = encode_base64_url(json.dumps(payload, separators=(",", ":")).encode())
    token_data = f"{header_base64}.{payload_base64}"
    signature = hmac.new(
        SECRET_KEY.encode(),
        token_data.encode(),
        sha256,
    ).digest()
    signature_base64 = encode_base64_url(signature)
    return f"{token_data}.{signature_base64}"


def decode_access_token(token: str) -> dict:
    try:
        header_base64, payload_base64, signature_base64 = token.split(".")
    except ValueError as exc:
        raise ValueError("Invalid token format") from exc

    token_data = f"{header_base64}.{payload_base64}"
    expected_signature = hmac.new(
        SECRET_KEY.encode(),
        token_data.encode(),
        sha256,
    ).digest()
    expected_signature_base64 = encode_base64_url(expected_signature)

    if not hmac.compare_digest(signature_base64, expected_signature_base64):
        raise ValueError("Invalid token signature")

    payload = json.loads(decode_base64_url(payload_base64))
    if int(payload["exp"]) < int(time.time()):
        raise ValueError("Token has expired")

    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return {
        "id": int(payload["sub"]),
        "email": payload["email"],
        "full_name": payload["full_name"],
        "roles": payload["roles"],
        "exp": payload["exp"],
    }


def require_roles(*allowed_roles: str) -> Callable:
    def check_role(current_user: dict = Depends(get_current_user)) -> dict:
        user_roles = set(current_user["roles"])
        if not user_roles.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        return current_user

    return check_role
