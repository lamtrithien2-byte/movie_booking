from sqlalchemy.orm import Session

from app.repositories import repo_booking
from app.services.service_pagination import paginate_data


def booking_data(booking) -> dict:
    showtime = booking.showtime
    movie = showtime.movie
    cinema = showtime.cinema
    room = showtime.room
    seats = sorted(seat.seat_code for seat in booking.seats)

    return {
        "id": booking.id,
        "ticket_code": f"BK{booking.id:06d}",
        "status": booking.status,
        "booked_at": booking.created_at,
        "user": user_data(booking.user),
        "movie": {
            "id": movie.id,
            "title": movie.title,
            "duration": movie.duration,
            "type": movie.type,
        },
        "cinema": {
            "id": cinema.id,
            "name": cinema.name,
            "address": cinema.address,
            "city": cinema.city,
            "district": cinema.district,
        },
        "room": {
            "id": room.id,
            "name": room.name,
        } if room else None,
        "showtime": {
            "id": showtime.id,
            "date": showtime.start_time.strftime("%d/%m/%Y"),
            "time": showtime.start_time.strftime("%H:%M"),
            "start_time": showtime.start_time,
        },
        "seats": seats,
        "total_seats": len(seats),
    }


def user_data(user) -> dict | None:
    if user is None:
        return None
    return {
        "full_name": user.full_name,
        "phone": user.phone,
    }


def list_bookings(
    db: Session,
    page: int,
    size: int,
    movie_id: int | None = None,
    cinema_id: int | None = None,
    showtime_id: int | None = None,
) -> dict:
    query = repo_booking.get_bookings(db, movie_id, cinema_id, showtime_id)
    return paginate_data(query, page, size, booking_data)
