from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import repo_cinema, repo_room
from app.services.service_pagination import paginate_data


def total_seats(room) -> int:
    return room.total_rows * room.total_cols


def room_data(room) -> dict:
    return {
        "id": room.id,
        "cinema_id": room.cinema_id,
        "cinema_name": room.cinema.name if room.cinema else None,
        "city": room.cinema.city if room.cinema else None,
        "district": room.cinema.district if room.cinema else None,
        "name": room.name,
        "total_rows": room.total_rows,
        "total_cols": room.total_cols,
        "total_seats": total_seats(room),
        "is_active": room.is_active,
    }


def user_room_data(room) -> dict:
    return {
        "id": room.id,
        "cinema_name": room.cinema.name if room.cinema else None,
        "city": room.cinema.city if room.cinema else None,
        "district": room.cinema.district if room.cinema else None,
        "name": room.name,
        "total_rows": room.total_rows,
        "total_cols": room.total_cols,
        "total_seats": total_seats(room),
    }


def list_rooms(
    db: Session,
    page: int,
    size: int,
    only_active: bool = True,
    cinema_id: int | None = None,
    showtime_id: int | None = None,
    cinema_name: str | None = None,
    city: str | None = None,
    district: str | None = None,
    user_view: bool = False,
) -> dict:
    has_city = bool(city and city.strip())
    has_district = bool(district and district.strip())

    if has_district and not has_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please choose city before choosing district",
        )

    query = (
        repo_room.get_active_rooms(db, cinema_id, showtime_id, cinema_name, city, district)
        if only_active
        else repo_room.get_rooms(db, cinema_id, showtime_id, cinema_name, city, district)
    )
    data_func = user_room_data if user_view else room_data
    return paginate_data(query, page, size, data_func)


def get_room(db: Session, room_id: int, only_active: bool = True, user_view: bool = False) -> dict:
    room = repo_room.get_room_by_id(db, room_id)
    if room is None or (only_active and not room.is_active):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return user_room_data(room) if user_view else room_data(room)


def check_cinema(db: Session, cinema_id: int) -> None:
    if repo_cinema.get_cinema_by_id(db, cinema_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cinema not found")


def check_duplicate_room(db: Session, cinema_id: int, name: str, room_id: int | None = None) -> None:
    room = repo_room.get_room_by_cinema_and_name(db, cinema_id, name)
    if room and room.id != room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room name already exists in this cinema",
        )


def create_room(db: Session, data: dict) -> dict:
    check_cinema(db, data["cinema_id"])
    check_duplicate_room(db, data["cinema_id"], data["name"])
    return room_data(repo_room.create_room(db, data))


def update_room(db: Session, room_id: int, data: dict) -> dict:
    room = repo_room.get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    check_cinema(db, data["cinema_id"])
    check_duplicate_room(db, data["cinema_id"], data["name"], room_id)
    return room_data(repo_room.update_room(db, room, data))


def delete_room(db: Session, room_id: int) -> dict:
    room = repo_room.get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    repo_room.delete_room(db, room)
    return {"message": "Room deleted successfully"}
