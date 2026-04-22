from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import repo_cinema
from app.services.service_pagination import paginate_data


def cinema_data(cinema) -> dict:
    return {
        "id": cinema.id,
        "name": cinema.name,
        "address": cinema.address,
        "city": cinema.city,
        "district": cinema.district,
        "is_active": cinema.is_active,
    }


def list_cinemas(
    db: Session,
    page: int,
    size: int,
    only_active: bool = True,
    city: str | None = None,
    district: str | None = None,
) -> dict:
    if district and district.strip() and not (city and city.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please choose city before choosing district",
        )

    query = (
        repo_cinema.get_active_cinemas(db, city, district)
        if only_active
        else repo_cinema.get_cinemas(db, city, district)
    )
    return paginate_data(query, page, size, cinema_data)


def get_cinema(db: Session, cinema_id: int, only_active: bool = True) -> dict:
    cinema = repo_cinema.get_cinema_by_id(db, cinema_id)
    if cinema is None or (only_active and not cinema.is_active):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cinema not found")
    return cinema_data(cinema)


def create_cinema(db: Session, data: dict) -> dict:
    return cinema_data(repo_cinema.create_cinema(db, data))


def update_cinema(db: Session, cinema_id: int, data: dict) -> dict:
    cinema = repo_cinema.get_cinema_by_id(db, cinema_id)
    if cinema is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cinema not found")
    return cinema_data(repo_cinema.update_cinema(db, cinema, data))


def delete_cinema(db: Session, cinema_id: int) -> dict:
    cinema = repo_cinema.get_cinema_by_id(db, cinema_id)
    if cinema is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cinema not found")
    repo_cinema.delete_cinema(db, cinema)
    return {"message": "Cinema deleted successfully"}
