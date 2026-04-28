from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.db_database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    method = Column(String(30), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    order_code = Column(BigInteger, unique=True, nullable=True)
    original_amount = Column(Integer, nullable=False)
    discount_amount = Column(Integer, default=0, nullable=False)
    final_amount = Column(Integer, nullable=False)
    voucher_code = Column(String(50), nullable=True)
    checkout_url = Column(String(500), nullable=True)
    qr_code = Column(Text, nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    booking = relationship("Booking")


class Voucher(Base):
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_type = Column(String(20), nullable=False)
    discount_value = Column(Integer, nullable=False)
    min_order_amount = Column(Integer, default=0, nullable=False)
    max_discount = Column(Integer, nullable=True)
    quantity = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
