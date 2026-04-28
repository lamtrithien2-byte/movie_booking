from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import repo_cinema, repo_movie, repo_room, repo_showtime
from app.services.service_pagination import paginate_data


def show_date_text(start_time) -> str:
    return start_time.strftime("%d/%m/%Y")


def show_time_text(start_time) -> str:
    return start_time.strftime("%H:%M")


def showtime_data(showtime) -> dict:
    return {
        "id": showtime.id,
        "movie_id": showtime.movie_id,
        "movie_title": showtime.movie.title if showtime.movie else None,
        "cinema_id": showtime.cinema_id,
        "cinema_name": showtime.cinema.name if showtime.cinema else None,
        "room_id": showtime.room_id,
        "room_name": showtime.room.name if showtime.room else None,
        "city": showtime.cinema.city if showtime.cinema else None,
        "district": showtime.cinema.district if showtime.cinema else None,
        "start_time": showtime.start_time,
        "show_date": show_date_text(showtime.start_time),
        "show_time": show_time_text(showtime.start_time),
        "is_active": showtime.is_active,
    }


def user_showtime_data(showtime) -> dict:
    return {
        "id": showtime.id,
        "movie_title": showtime.movie.title if showtime.movie else None,
        "cinema_name": showtime.cinema.name if showtime.cinema else None,
        "room_name": showtime.room.name if showtime.room else None,
        "city": showtime.cinema.city if showtime.cinema else None,
        "district": showtime.cinema.district if showtime.cinema else None,
        "date": show_date_text(showtime.start_time),
        "time": show_time_text(showtime.start_time),
    }


def list_showtimes(
    db: Session,
    page: int,
    size: int,
    only_active: bool = True,
    movie_id: int | None = None,
    movie_title: str | None = None,
    cinema_id: int | None = None,
    room_id: int | None = None,
    city: str | None = None,
    district: str | None = None,
    show_date: date | None = None,
    user_view: bool = False,
) -> dict:
    has_city = bool(city and city.strip())
    has_district = bool(district and district.strip())

    if has_district and not has_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui long chon thanh pho truoc khi chon quan",
        )

    query = (
        repo_showtime.get_active_showtimes(
            db,
            movie_id,
            movie_title,
            cinema_id,
            room_id,
            city,
            district,
            show_date,
        )
        if only_active
        else repo_showtime.get_showtimes(
            db,
            movie_id,
            movie_title,
            cinema_id,
            room_id,
            city,
            district,
            show_date,
        )
    )
    data_func = user_showtime_data if user_view else showtime_data
    return paginate_data(query, page, size, data_func)


def get_showtime(
    db: Session,
    showtime_id: int,
    only_active: bool = True,
    user_view: bool = False,
) -> dict:
    showtime = repo_showtime.get_showtime_by_id(db, showtime_id)
    if showtime is None or (only_active and not showtime.is_active):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay suat chieu")
    return user_showtime_data(showtime) if user_view else showtime_data(showtime)


def check_movie_cinema_and_room(
    db: Session,
    movie_id: int,
    cinema_id: int,
    room_id: int,
) -> None:
    if repo_movie.get_movie_by_id(db, movie_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay phim")

    if repo_cinema.get_cinema_by_id(db, cinema_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay rap")

    room = repo_room.get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay phong")

    if room.cinema_id != cinema_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phong khong thuoc rap nay",
        )


def create_showtime(db: Session, data: dict) -> dict:
    check_movie_cinema_and_room(db, data["movie_id"], data["cinema_id"], data["room_id"])
    return showtime_data(repo_showtime.create_showtime(db, data))


def update_showtime(db: Session, showtime_id: int, data: dict) -> dict:
    showtime = repo_showtime.get_showtime_by_id(db, showtime_id)
    if showtime is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay suat chieu")

    check_movie_cinema_and_room(db, data["movie_id"], data["cinema_id"], data["room_id"])
    return showtime_data(repo_showtime.update_showtime(db, showtime, data))


def delete_showtime(db: Session, showtime_id: int) -> dict:
    showtime = repo_showtime.get_showtime_by_id(db, showtime_id)
    if showtime is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay suat chieu")
    repo_showtime.delete_showtime(db, showtime)
    return {"message": "Da xoa suat chieu"}
