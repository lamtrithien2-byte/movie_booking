from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import repo_movie
from app.services.service_pagination import paginate_query


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
) -> dict:
    query = (
        repo_movie.get_active_movies(db, keyword, movie_type)
        if only_active
        else repo_movie.get_movies(db, keyword, movie_type)
    )
    movies, pagination = paginate_query(query, page, size)
    return {
        "data": [movie_data(movie) for movie in movies],
        "pagination": pagination,
    }


def get_movie(db: Session, movie_id: int, only_active: bool = True) -> dict:
    movie = repo_movie.get_movie_by_id(db, movie_id)
    if movie is None or (only_active and not movie.is_active):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie_data(movie)


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
