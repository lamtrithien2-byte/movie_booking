from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import repo_movie, repo_showtime
from app.services.service_pagination import paginate_data


def movie_data(movie) -> dict:
    return {
        "id": movie.id,
        "title": movie.title,
        "description": movie.description,
        "duration": movie.duration,
        "type": movie.type,
        "is_active": movie.is_active,
    }


def list_movies(
    db: Session,
    page: int,
    size: int,
    only_active: bool = True,
    keyword: str | None = None,
    movie_type: str | None = None,
    with_schedule: bool = False,
) -> dict:
    query = (
        repo_movie.get_active_movies(db, keyword, movie_type)
        if only_active
        else repo_movie.get_movies(db, keyword, movie_type)
    )
    data_func = movie_full_data(db) if with_schedule else movie_data
    return paginate_data(query, page, size, data_func)


def get_movie(db: Session, movie_id: int, only_active: bool = True) -> dict:
    movie = repo_movie.get_movie_by_id(db, movie_id)
    if movie is None or (only_active and not movie.is_active):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie_data(movie)


def movie_full_data(db: Session):
    def build(movie) -> dict:
        data = movie_data(movie)
        data["cinemas"] = movie_cinemas(db, movie)
        return data

    return build


def movie_cinemas(db: Session, movie) -> list[dict]:
    showtimes = repo_showtime.get_active_showtimes(
        db,
        movie_id=movie.id,
    ).all()

    cinemas = {}
    for showtime in showtimes:
        cinema = showtime.cinema
        room = showtime.room
        if cinema is None:
            continue

        if cinema.id not in cinemas:
            cinemas[cinema.id] = {
                "id": cinema.id,
                "name": cinema.name,
                "address": cinema.address,
                "city": cinema.city,
                "district": cinema.district,
                "showtimes": [],
            }

        cinemas[cinema.id]["showtimes"].append(
            {
                "id": showtime.id,
                "date": showtime.start_time.strftime("%d/%m/%Y"),
                "time": showtime.start_time.strftime("%H:%M"),
                "room": {
                    "id": room.id if room else None,
                    "name": room.name if room else None,
                },
            }
        )

    return list(cinemas.values())


def create_movie(db: Session, data: dict) -> dict:
    return movie_data(repo_movie.create_movie(db, data))


def update_movie(db: Session, movie_id: int, data: dict) -> dict:
    movie = repo_movie.get_movie_by_id(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie_data(repo_movie.update_movie(db, movie, data))


def delete_movie(db: Session, movie_id: int) -> dict:
    movie = repo_movie.get_movie_by_id(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    repo_movie.delete_movie(db, movie)
    return {"message": "Movie deleted successfully"}
