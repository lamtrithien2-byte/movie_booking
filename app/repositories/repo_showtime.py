from datetime import date, datetime, time, timedelta
import re

from sqlalchemy.orm import Session

from app.models.model_cinema import Cinema
from app.models.model_movie import Movie
from app.models.model_showtime import Showtime


def filter_showtimes(
    query,
    movie_id: int | None = None,
    movie_title: str | None = None,
    cinema_id: int | None = None,
    room_id: int | None = None,
    city: str | None = None,
    district: str | None = None,
    show_date: date | None = None,
):
    if movie_id:
        query = query.filter(Showtime.movie_id == movie_id)
    if movie_title and movie_title.strip():
        search_words = re.findall(r"\w+", movie_title.strip())
        if search_words:
            query = query.join(Movie, Showtime.movie_id == Movie.id)
            for word in search_words:
                query = query.filter(Movie.title.ilike(f"%{word}%"))
    if cinema_id:
        query = query.filter(Showtime.cinema_id == cinema_id)
    if room_id:
        query = query.filter(Showtime.room_id == room_id)
    if city and city.strip():
        query = query.join(Cinema, Showtime.cinema_id == Cinema.id)
        query = query.filter(Cinema.city.ilike(f"%{city.strip()}%"))
        if district and district.strip():
            query = query.filter(Cinema.district.ilike(f"%{district.strip()}%"))
    if show_date:
        start_day = datetime.combine(show_date, time.min)
        end_day = start_day + timedelta(days=1)
        query = query.filter(Showtime.start_time >= start_day, Showtime.start_time < end_day)
    return query


def get_showtimes(
    db: Session,
    movie_id: int | None = None,
    movie_title: str | None = None,
    cinema_id: int | None = None,
    room_id: int | None = None,
    city: str | None = None,
    district: str | None = None,
    show_date: date | None = None,
):
    query = filter_showtimes(
        db.query(Showtime),
        movie_id,
        movie_title,
        cinema_id,
        room_id,
        city,
        district,
        show_date,
    )
    return query.order_by(Showtime.start_time)


def get_active_showtimes(
    db: Session,
    movie_id: int | None = None,
    movie_title: str | None = None,
    cinema_id: int | None = None,
    room_id: int | None = None,
    city: str | None = None,
    district: str | None = None,
    show_date: date | None = None,
):
    query = db.query(Showtime).filter(Showtime.is_active.is_(True))
    query = filter_showtimes(query, movie_id, movie_title, cinema_id, room_id, city, district, show_date)
    return query.order_by(Showtime.start_time)


def get_showtime_by_id(db: Session, showtime_id: int):
    return db.query(Showtime).filter(Showtime.id == showtime_id).first()


def create_showtime(db: Session, data: dict):
    showtime = Showtime(**data)
    db.add(showtime)
    db.commit()
    db.refresh(showtime)
    return showtime


def update_showtime(db: Session, showtime: Showtime, data: dict):
    for key, value in data.items():
        setattr(showtime, key, value)
    db.commit()
    db.refresh(showtime)
    return showtime


def delete_showtime(db: Session, showtime: Showtime):
    db.delete(showtime)
    db.commit()
