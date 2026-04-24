from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.db_database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    showtime_id = Column(Integer, ForeignKey("showtimes.id"), nullable=False)
    status = Column(String(20), default="booked", nullable=False)
    pending_seats = Column(Text, nullable=True)
    pending_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    showtime = relationship("Showtime")
    seats = relationship("Seat", back_populates="booking")
