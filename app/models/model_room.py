from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.db_database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    cinema_id = Column(Integer, ForeignKey("cinemas.id"), nullable=False)
    name = Column(String(100), nullable=False)
    total_rows = Column(Integer, nullable=False)
    total_cols = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cinema = relationship("Cinema")

    __table_args__ = (
        UniqueConstraint("cinema_id", "name", name="uq_rooms_cinema_name"),
    )
