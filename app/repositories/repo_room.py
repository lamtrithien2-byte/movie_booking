from sqlalchemy.orm import Session

from app.models.model_cinema import Cinema
from app.models.model_room import Room
from app.models.model_showtime import Showtime


def filter_rooms(
    query,
    cinema_id: int | None = None,
    showtime_id: int | None = None,
    cinema_name: str | None = None,
    city: str | None = None,
    district: str | None = None,
):
    if cinema_id:
        query = query.filter(Room.cinema_id == cinema_id)

    if showtime_id:
        query = query.join(Showtime, Room.id == Showtime.room_id)
        query = query.filter(Showtime.id == showtime_id)

    has_cinema_filter = (
        cinema_name and cinema_name.strip()
        or city and city.strip()
        or district and district.strip()
    )

    if has_cinema_filter:
        query = query.join(Cinema, Room.cinema_id == Cinema.id)

        if cinema_name and cinema_name.strip():
            query = query.filter(Cinema.name.ilike(f"%{cinema_name.strip()}%"))
        if city and city.strip():
            query = query.filter(Cinema.city.ilike(f"%{city.strip()}%"))
        if district and district.strip():
            query = query.filter(Cinema.district.ilike(f"%{district.strip()}%"))

    return query


def get_rooms(
    db: Session,
    cinema_id: int | None = None,
    showtime_id: int | None = None,
    cinema_name: str | None = None,
    city: str | None = None,
    district: str | None = None,
):
    query = filter_rooms(db.query(Room), cinema_id, showtime_id, cinema_name, city, district)
    return query.order_by(Room.id)


def get_active_rooms(
    db: Session,
    cinema_id: int | None = None,
    showtime_id: int | None = None,
    cinema_name: str | None = None,
    city: str | None = None,
    district: str | None = None,
):
    query = db.query(Room).filter(Room.is_active.is_(True))
    query = filter_rooms(query, cinema_id, showtime_id, cinema_name, city, district)
    return query.order_by(Room.id)


def get_room_by_id(db: Session, room_id: int):
    return db.query(Room).filter(Room.id == room_id).first()


def get_room_by_cinema_and_name(db: Session, cinema_id: int, name: str):
    return db.query(Room).filter(Room.cinema_id == cinema_id, Room.name.ilike(name)).first()


def create_room(db: Session, data: dict):
    room = Room(**data)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def update_room(db: Session, room: Room, data: dict):
    for key, value in data.items():
        setattr(room, key, value)
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room: Room):
    db.delete(room)
    db.commit()
