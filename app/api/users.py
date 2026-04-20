from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.models.model_user import User
from app.services.service_auth import require_roles
from app.services.service_pagination import paginate_query

router = APIRouter(prefix="/admin/users", tags=["users"])


class PaginationData(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int


class UserItem(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None
    roles: list[str]
    is_active: bool


class UsersResponse(BaseModel):
    data: list[UserItem]
    pagination: PaginationData


@router.get("", response_model=UsersResponse)
def get_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    query = (
        db.query(User)
        .order_by(User.id)
    )
    users, pagination = paginate_query(query, page, size)

    return {
        "data": [
            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "roles": [role.name for role in user.roles],
                "is_active": user.is_active,
            }
            for user in users
        ],
        "pagination": pagination,
    }
