from datetime import date, datetime, time

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.services import service_showtime
from app.services.service_auth import require_roles

router = APIRouter(tags=["showtimes"])


class ShowtimeRequest(BaseModel):
    movie_id: int = Field(gt=0)
    cinema_id: int = Field(gt=0)
    room_id: int = Field(gt=0)
    show_date: str = Field(examples=["22/04/2026"], description="Format: dd/mm/yyyy")
    show_time: str = Field(examples=["20:30"], description="Format: HH:MM")
    is_active: bool = True

    @field_validator("show_date")
    @classmethod
    def validate_show_date(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError as exc:
            raise ValueError("show_date must be dd/mm/yyyy, example: 22/04/2026") from exc
        return value

    @field_validator("show_time")
    @classmethod
    def validate_show_time(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError("show_time must be HH:MM, example: 20:30") from exc
        return value

    def to_data(self) -> dict:
        show_date = datetime.strptime(self.show_date, "%d/%m/%Y").date()
        show_time = datetime.strptime(self.show_time, "%H:%M").time()
        return {
            "movie_id": self.movie_id,
            "cinema_id": self.cinema_id,
            "room_id": self.room_id,
            "start_time": datetime.combine(show_date, show_time),
            "is_active": self.is_active,
        }

    model_config = {
        "json_schema_extra": {
            "example": {
                "movie_id": 1,
                "cinema_id": 1,
                "room_id": 1,
                "show_date": "22/04/2026",
                "show_time": "20:30",
                "is_active": True,
            }
        }
    }


class ShowtimeResponse(BaseModel):
    id: int
    movie_id: int
    movie_title: str | None
    cinema_id: int
    cinema_name: str | None
    room_id: int | None
    room_name: str | None
    city: str | None
    district: str | None
    start_time: datetime
    show_date: str
    show_time: str
    is_active: bool


class UserShowtimeResponse(BaseModel):
    id: int
    movie_title: str | None
    cinema_name: str | None
    room_name: str | None
    city: str | None
    district: str | None
    date: str
    time: str


@router.get("/showtimes")
def get_showtimes(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    movie_title: str | None = Query(default=None, description="Search showtimes by movie title"),
    cinema_id: int | None = Query(default=None, gt=0, description="Filter by selected cinema"),
    city: str | None = Query(default=None, description="Filter by cinema city"),
    district: str | None = Query(default=None, description="Filter by cinema district"),
    show_date: date | None = Query(default=None, alias="date", description="Filter by show date"),
    db: Session = Depends(get_db),
):
    return service_showtime.list_showtimes(
        db,
        page,
        size,
        only_active=True,
        movie_title=movie_title,
        cinema_id=cinema_id,
        city=city,
        district=district,
        show_date=show_date,
        user_view=True,
    )


@router.get("/showtimes/{showtime_id}", response_model=UserShowtimeResponse)
def get_showtime_detail(
    showtime_id: int,
    db: Session = Depends(get_db),
):
    return service_showtime.get_showtime(db, showtime_id, only_active=True, user_view=True)


@router.get("/admin/showtimes")
def get_admin_showtimes(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    movie_id: int | None = Query(default=None, gt=0),
    movie_title: str | None = Query(default=None, description="Search showtimes by movie title"),
    cinema_id: int | None = Query(default=None, gt=0),
    room_id: int | None = Query(default=None, gt=0),
    city: str | None = Query(default=None, description="Filter by cinema city"),
    district: str | None = Query(default=None, description="Filter by cinema district"),
    show_date: date | None = Query(default=None, alias="date", description="Filter by show date"),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_showtime.list_showtimes(
        db,
        page,
        size,
        only_active=False,
        movie_id=movie_id,
        movie_title=movie_title,
        cinema_id=cinema_id,
        room_id=room_id,
        city=city,
        district=district,
        show_date=show_date,
    )


@router.post("/admin/showtimes", status_code=status.HTTP_201_CREATED, response_model=ShowtimeResponse)
def create_admin_showtime(
    body: ShowtimeRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_showtime.create_showtime(db, body.to_data())


@router.put("/admin/showtimes/{showtime_id}", response_model=ShowtimeResponse)
def update_admin_showtime(
    showtime_id: int,
    body: ShowtimeRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_showtime.update_showtime(db, showtime_id, body.to_data())


@router.delete("/admin/showtimes/{showtime_id}")
def delete_admin_showtime(
    showtime_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_showtime.delete_showtime(db, showtime_id)
