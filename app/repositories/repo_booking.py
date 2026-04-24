from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.model_booking import Booking
from app.models.model_showtime import Showtime


def create_booking(
    db: Session,
    showtime_id: int,
    user_id: int | None = None,
    status: str = "pending_payment",
    pending_seats: str | None = None,
    pending_expires_at=None,
):
    booking = Booking(
        showtime_id=showtime_id,
        user_id=user_id,
        status=status,
        pending_seats=pending_seats,
        pending_expires_at=pending_expires_at,
    )
    db.add(booking)
    db.flush()
    return booking


def get_booking_by_id(db: Session, booking_id: int):
    return db.query(Booking).filter(Booking.id == booking_id).first()


def get_active_pending_bookings(db: Session, showtime_id: int):
    now = datetime.now(timezone.utc)
    return (
        db.query(Booking)
        .filter(Booking.showtime_id == showtime_id)
        .filter(Booking.status == "pending_payment")
        .filter(Booking.pending_seats.isnot(None))
        .filter(Booking.pending_expires_at.isnot(None))
        .filter(Booking.pending_expires_at > now)
        .all()
    )


def expire_pending_bookings(
    db: Session,
    showtime_id: int | None = None,
    booking_id: int | None = None,
) -> bool:
    now = datetime.now(timezone.utc)
    query = (
        db.query(Booking)
        .filter(Booking.status == "pending_payment")
        .filter(Booking.pending_seats.isnot(None))
        .filter(Booking.pending_expires_at.isnot(None))
        .filter(Booking.pending_expires_at <= now)
    )

    if showtime_id is not None:
        query = query.filter(Booking.showtime_id == showtime_id)
    if booking_id is not None:
        query = query.filter(Booking.id == booking_id)

    bookings = query.all()
    if not bookings:
        return False

    for booking in bookings:
        booking.status = "expired"
        booking.pending_seats = None
        booking.pending_expires_at = None

    db.flush()
    return True


def get_booking_detail_by_id(db: Session, booking_id: int):
    row = db.execute(
        text("SELECT * FROM booking_details WHERE booking_id = :booking_id"),
        {"booking_id": booking_id},
    ).mappings().first()
    return dict(row) if row else None


def get_bookings(
    db: Session,
    movie_id: int | None = None,
    cinema_id: int | None = None,
    showtime_id: int | None = None,
):
    query = db.query(Booking).join(Showtime, Booking.showtime_id == Showtime.id)

    if movie_id:
        query = query.filter(Showtime.movie_id == movie_id)
    if cinema_id:
        query = query.filter(Showtime.cinema_id == cinema_id)
    if showtime_id:
        query = query.filter(Booking.showtime_id == showtime_id)

    return query.order_by(Booking.created_at.desc())
