from sqlalchemy.orm import Session

from app.models.model_cinema import Cinema


def filter_cinemas(
    query,
    city: str | None = None,
    district: str | None = None,
):
    if city and city.strip():
        query = query.filter(Cinema.city.ilike(f"%{city.strip()}%"))
    if district and district.strip():
        query = query.filter(Cinema.district.ilike(f"%{district.strip()}%"))
    return query


def get_cinemas(
    db: Session,
    city: str | None = None,
    district: str | None = None,
):
    query = filter_cinemas(db.query(Cinema), city, district)
    return query.order_by(Cinema.id)


def get_active_cinemas(
    db: Session,
    city: str | None = None,
    district: str | None = None,
):
    query = db.query(Cinema).filter(Cinema.is_active.is_(True))
    query = filter_cinemas(query, city, district)
    return query.order_by(Cinema.id)


def get_cinema_by_id(db: Session, cinema_id: int):
    return db.query(Cinema).filter(Cinema.id == cinema_id).first()


def create_cinema(db: Session, data: dict):
    cinema = Cinema(**data)
    db.add(cinema)
    db.commit()
    db.refresh(cinema)
    return cinema


def update_cinema(db: Session, cinema: Cinema, data: dict):
    for key, value in data.items():
        setattr(cinema, key, value)
    db.commit()
    db.refresh(cinema)
    return cinema


def delete_cinema(db: Session, cinema: Cinema):
    db.delete(cinema)
    db.commit()
