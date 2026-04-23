import re

from sqlalchemy.orm import Session

from app.models.model_movie import Movie


def filter_movies(query, keyword: str | None = None, movie_type: str | None = None):
    if keyword and keyword.strip():
        search_words = re.findall(r"\w+", keyword.strip())
        for word in search_words:
            query = query.filter(Movie.title.ilike(f"%{word}%"))
    if movie_type and movie_type.strip():
        query = query.filter(Movie.type.ilike(f"%{movie_type.strip()}%"))
    return query


def get_movies(db: Session, keyword: str | None = None, movie_type: str | None = None):
    query = filter_movies(db.query(Movie), keyword, movie_type)
    return query.order_by(Movie.id)


def get_active_movies(db: Session, keyword: str | None = None, movie_type: str | None = None):
    query = db.query(Movie).filter(Movie.is_active.is_(True))
    query = filter_movies(query, keyword, movie_type)
    return query.order_by(Movie.id)


def get_movie_by_id(db: Session, movie_id: int):
    return db.query(Movie).filter(Movie.id == movie_id).first()


def create_movie(db: Session, data: dict):
    movie = Movie(**data)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def update_movie(db: Session, movie: Movie, data: dict):
    for key, value in data.items():
        setattr(movie, key, value)
    db.commit()
    db.refresh(movie)
    return movie


def delete_movie(db: Session, movie: Movie):
    db.delete(movie)
    db.commit()
