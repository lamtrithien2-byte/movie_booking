from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.models.model_role import Role
from app.services.service_auth import require_roles
from app.services.service_pagination import paginate_query

router = APIRouter(prefix="/admin/roles", tags=["roles"])


class PaginationData(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int


class RoleItem(BaseModel):
    id: int
    name: str


class RolesResponse(BaseModel):
    data: list[RoleItem]
    pagination: PaginationData


@router.get("", response_model=RolesResponse)
def get_roles(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    query = (
        db.query(Role)
        .order_by(Role.id)
    )
    roles, pagination = paginate_query(query, page, size)

    return {
        "data": [{"id": role.id, "name": role.name} for role in roles],
        "pagination": pagination,
    }
