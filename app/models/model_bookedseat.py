from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.db_database import Base


class BookedSeat(Base):
    __tablename__ = "booked_seats"

    id = Column(Integer, primary_key=True, index=True)
    showtime_id = Column(Integer, ForeignKey("showtimes.id"), nullable=False)
    seat_code = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    showtime = relationship("Showtime")

    __table_args__ = (
        UniqueConstraint("showtime_id", "seat_code", name="uq_booked_seats_showtime_seat"),
    )
