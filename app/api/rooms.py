from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.services import service_room
from app.services.service_auth import require_roles

router = APIRouter(tags=["rooms"])


class RoomRequest(BaseModel):
    cinema_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100, examples=["Room 1"])
    total_rows: int = Field(gt=0, le=50, examples=[10])
    total_cols: int = Field(gt=0, le=50, examples=[12])
    is_active: bool = True


class RoomResponse(BaseModel):
    id: int
    cinema_id: int
    cinema_name: str | None
    city: str | None
    district: str | None
    name: str
    total_rows: int
    total_cols: int
    total_seats: int
    is_active: bool


class UserRoomResponse(BaseModel):
    id: int
    cinema_name: str | None
    city: str | None
    district: str | None
    name: str
    total_rows: int
    total_cols: int
    total_seats: int


@router.get("/rooms")
def get_rooms(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    cinema_id: int | None = Query(default=None, gt=0, description="Find rooms in one cinema"),
    showtime_id: int | None = Query(default=None, gt=0, description="Find room of one showtime"),
    db: Session = Depends(get_db),
):
    return service_room.list_rooms(
        db,
        page,
        size,
        only_active=True,
        cinema_id=cinema_id,
        showtime_id=showtime_id,
        user_view=True,
    )


@router.get("/rooms/{room_id}", response_model=UserRoomResponse)
def get_room_detail(
    room_id: int,
    db: Session = Depends(get_db),
):
    return service_room.get_room(db, room_id, only_active=True, user_view=True)


@router.get("/admin/rooms")
def get_admin_rooms(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    cinema_id: int | None = Query(default=None, gt=0),
    showtime_id: int | None = Query(default=None, gt=0),
    cinema_name: str | None = Query(default=None, description="Search rooms by cinema name"),
    city: str | None = Query(default=None, description="Filter by city"),
    district: str | None = Query(default=None, description="Filter by district"),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_room.list_rooms(
        db,
        page,
        size,
        only_active=False,
        cinema_id=cinema_id,
        showtime_id=showtime_id,
        cinema_name=cinema_name,
        city=city,
        district=district,
    )


@router.post("/admin/rooms", status_code=status.HTTP_201_CREATED, response_model=RoomResponse)
def create_admin_room(
    body: RoomRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_room.create_room(db, body.model_dump())


@router.put("/admin/rooms/{room_id}", response_model=RoomResponse)
def update_admin_room(
    room_id: int,
    body: RoomRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_room.update_room(db, room_id, body.model_dump())


@router.delete("/admin/rooms/{room_id}")
def delete_admin_room(
    room_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_room.delete_room(db, room_id)
