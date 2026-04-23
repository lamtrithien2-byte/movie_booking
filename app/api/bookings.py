from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.services import service_booking
from app.services.service_auth import require_roles

router = APIRouter(prefix="/admin/bookings", tags=["bookings"])


@router.get("")
def get_bookings(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    movie_id: int | None = Query(default=None, gt=0),
    cinema_id: int | None = Query(default=None, gt=0),
    showtime_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_booking.list_bookings(
        db,
        page,
        size,
        movie_id=movie_id,
        cinema_id=cinema_id,
        showtime_id=showtime_id,
    )
