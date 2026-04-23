from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.services.service_auth import require_roles
from app.services import service_movie

router = APIRouter(tags=["movies"])


class MovieRequest(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str | None = None
    duration: int = Field(gt=0)
    type: str | None = Field(default=None, max_length=100)
    is_active: bool = True


class MovieResponse(BaseModel):
    id: int
    title: str
    description: str | None
    duration: int
    type: str | None
    is_active: bool


@router.get("/movies")
def get_movies(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = Query(default=None, description="Search movie by title"),
    movie_type: str | None = Query(default=None, alias="type", description="Search movie by type"),
    db: Session = Depends(get_db),
):
    return service_movie.list_movies(
        db,
        page,
        size,
        only_active=True,
        keyword=keyword,
        movie_type=movie_type,
    )


@router.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie_detail(
    movie_id: int,
    db: Session = Depends(get_db),
):
    return service_movie.get_movie(db, movie_id, only_active=True)


@router.get("/admin/movies")
def get_admin_movies(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = Query(default=None, description="Search movie by title"),
    movie_type: str | None = Query(default=None, alias="type", description="Search movie by type"),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_movie.list_movies(
        db,
        page,
        size,
        only_active=False,
        keyword=keyword,
        movie_type=movie_type,
    )


@router.post("/admin/movies", status_code=status.HTTP_201_CREATED, response_model=MovieResponse)
def create_admin_movie(
    body: MovieRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_movie.create_movie(db, body.model_dump())


@router.put("/admin/movies/{movie_id}", response_model=MovieResponse)
def update_admin_movie(
    movie_id: int,
    body: MovieRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_movie.update_movie(db, movie_id, body.model_dump())


@router.delete("/admin/movies/{movie_id}")
def delete_admin_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_movie.delete_movie(db, movie_id)
