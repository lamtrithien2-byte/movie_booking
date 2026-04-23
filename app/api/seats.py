from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.services import service_seat, service_ticket

router = APIRouter(tags=["seats"])


class SeatRequest(BaseModel):
    selected_seats: list[str] = Field(default_factory=list)


@router.get("/showtimes/{showtime_id}/seats")
def get_seats(showtime_id: int, db: Session = Depends(get_db)):
    return service_seat.get_seats(db, showtime_id)


@router.post("/showtimes/{showtime_id}/seats/select")
def select_seats(
    showtime_id: int,
    body: SeatRequest,
    db: Session = Depends(get_db),
):
    return service_seat.select_seats(db, showtime_id, body.selected_seats)


@router.post("/showtimes/{showtime_id}/seats/book")
def book_seats(
    showtime_id: int,
    body: SeatRequest,
    db: Session = Depends(get_db),
):
    return service_seat.book_seats(db, showtime_id, body.selected_seats)


@router.get("/bookings/{booking_id}/ticket")
def download_ticket(booking_id: int, db: Session = Depends(get_db)):
    path = service_ticket.create_ticket_pdf(db, booking_id)
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=path.name,
    )
