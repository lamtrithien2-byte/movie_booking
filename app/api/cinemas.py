from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.services.service_auth import get_current_user, require_roles
from app.services import service_cinema

router = APIRouter(tags=["cinemas"])


class CinemaRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    address: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    is_active: bool = True


class CinemaResponse(BaseModel):
    id: int
    name: str
    address: str
    city: str
    district: str | None
    is_active: bool


@router.get("/cinemas")
def get_cinemas(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    city: str | None = Query(default=None, description="Filter cinema by city"),
    district: str | None = Query(default=None, description="Filter cinema by district"),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    return service_cinema.list_cinemas(
        db,
        page,
        size,
        only_active=True,
        city=city,
        district=district,
    )


@router.get("/cinemas/{cinema_id}", response_model=CinemaResponse)
def get_cinema_detail(
    cinema_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    return service_cinema.get_cinema(db, cinema_id, only_active=True)


@router.get("/admin/cinemas")
def get_admin_cinemas(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    city: str | None = Query(default=None, description="Filter cinema by city"),
    district: str | None = Query(default=None, description="Filter cinema by district"),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_cinema.list_cinemas(
        db,
        page,
        size,
        only_active=False,
        city=city,
        district=district,
    )


@router.post("/admin/cinemas", status_code=status.HTTP_201_CREATED, response_model=CinemaResponse)
def create_admin_cinema(
    body: CinemaRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_cinema.create_cinema(db, body.model_dump())


@router.put("/admin/cinemas/{cinema_id}", response_model=CinemaResponse)
def update_admin_cinema(
    cinema_id: int,
    body: CinemaRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_cinema.update_cinema(db, cinema_id, body.model_dump())


@router.delete("/admin/cinemas/{cinema_id}")
def delete_admin_cinema(
    cinema_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_cinema.delete_cinema(db, cinema_id)
