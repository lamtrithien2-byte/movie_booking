from sqlalchemy.orm import Session

from app.models.model_booking import Booking
from app.models.model_showtime import Showtime


def create_booking(db: Session, showtime_id: int, user_id: int | None = None):
    booking = Booking(showtime_id=showtime_id, user_id=user_id)
    db.add(booking)
    db.flush()
    return booking


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
