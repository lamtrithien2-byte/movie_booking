from sqlalchemy.orm import Session

from app.models.model_seat import Seat


def get_booked_seats(db: Session, showtime_id: int):
    return db.query(Seat).filter(Seat.showtime_id == showtime_id).all()


def create_booked_seats(
    db: Session,
    showtime_id: int,
    seat_codes: list[str],
    booking_id: int | None = None,
):
    booked_seats = [
        Seat(booking_id=booking_id, showtime_id=showtime_id, seat_code=seat_code)
        for seat_code in seat_codes
    ]
    db.add_all(booked_seats)
    return booked_seats
