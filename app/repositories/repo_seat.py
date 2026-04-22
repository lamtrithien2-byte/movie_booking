from sqlalchemy.orm import Session

from app.models.model_bookedseat import BookedSeat


def get_booked_seats(db: Session, showtime_id: int):
    return db.query(BookedSeat).filter(BookedSeat.showtime_id == showtime_id).all()


def create_booked_seats(db: Session, showtime_id: int, seat_codes: list[str]):
    booked_seats = [
        BookedSeat(showtime_id=showtime_id, seat_code=seat_code)
        for seat_code in seat_codes
    ]
    db.add_all(booked_seats)
    db.commit()
    return booked_seats
