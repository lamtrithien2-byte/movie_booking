import os
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import repo_booking, repo_payment, repo_seat

DEFAULT_TICKET_PRICE = int(os.getenv("DEFAULT_TICKET_PRICE", "90000"))


def payment_data(payment) -> dict:
    return {
        "id": payment.id,
        "booking_id": payment.booking_id,
        "method": payment.method,
        "status": payment.status,
        "original_amount": payment.original_amount,
        "discount_amount": payment.discount_amount,
        "final_amount": payment.final_amount,
        "voucher_code": payment.voucher_code,
        "paid_at": payment.paid_at,
        "ticket_url": f"/bookings/{payment.booking_id}/payments/ticket" if payment.status == "paid" else None,
    }


def voucher_data(voucher) -> dict:
    return {
        "id": voucher.id,
        "code": voucher.code,
        "discount_value": voucher.discount_value,
        "quantity": voucher.quantity,
        "used_count": voucher.used_count,
        "is_active": voucher.is_active,
        "expires_at": voucher.expires_at,
    }


def pending_seat_codes(booking) -> list[str]:
    return [seat for seat in (booking.pending_seats or "").split(",") if seat]


def normalize_voucher_code(code: str | None) -> str | None:
    return code.strip().upper() if code and code.strip() else None


def get_booking_for_payment(db: Session, booking_id: int):
    repo_booking.expire_pending_bookings(db, booking_id=booking_id)
    booking = repo_booking.get_booking_by_id(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay booking")
    if booking.status == "expired" or (
        booking.pending_expires_at and booking.pending_expires_at <= datetime.now(timezone.utc)
    ):
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Da het thoi gian giu ghe")
    if not pending_seat_codes(booking):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking chua co ghe")
    if booking.status == "paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking da thanh toan")
    return booking


def get_valid_voucher(db: Session, voucher_code: str | None, amount: int):
    voucher_code = normalize_voucher_code(voucher_code)
    if voucher_code is None:
        return None

    voucher = repo_payment.get_voucher_by_code(db, voucher_code)
    if voucher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay voucher")
    if not voucher.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voucher khong hoat dong")
    if voucher.expires_at and voucher.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voucher da het han")
    if voucher.quantity is not None and voucher.used_count >= voucher.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voucher da het luot dung")
    if amount < voucher.min_order_amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Don hang chua du dieu kien ap voucher")
    return voucher


def discount_amount(amount: int, voucher) -> int:
    if voucher is None:
        return 0

    if voucher.discount_type == "percent":
        discount = amount * voucher.discount_value // 100
        if voucher.max_discount is not None:
            discount = min(discount, voucher.max_discount)
        return discount

    return min(amount, voucher.discount_value)


def create_payment(db: Session, booking_id: int, data: dict) -> dict:
    booking = get_booking_for_payment(db, booking_id)
    seat_codes = pending_seat_codes(booking)
    amount = len(seat_codes) * DEFAULT_TICKET_PRICE
    voucher = get_valid_voucher(db, data.get("voucher_code"), amount)
    discount = discount_amount(amount, voucher)

    payment = repo_payment.create_payment(
        db,
        {
            "booking_id": booking.id,
            "method": data["payment_method"],
            "status": "paid",
            "original_amount": amount,
            "discount_amount": discount,
            "final_amount": amount - discount,
            "voucher_code": voucher.code if voucher else None,
        },
    )
    try:
        payment.paid_at = datetime.now(timezone.utc)
        booking.status = "paid"
        booking.pending_seats = None
        booking.pending_expires_at = None
        repo_seat.create_booked_seats(db, booking.showtime_id, seat_codes, booking.id)

        if voucher is not None:
            voucher.used_count += 1

        db.commit()
        db.refresh(payment)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ghe vua duoc nguoi khac dat") from exc

    return payment_data(payment)


def create_voucher(db: Session, data: dict) -> dict:
    code = normalize_voucher_code(data["code"])
    if repo_payment.get_voucher_by_code(db, code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voucher da ton tai")

    if data["discount_value"] > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phan tram giam gia khong duoc qua 100")

    voucher = repo_payment.create_voucher(
        db,
        {
            "code": code,
            "discount_type": "percent",
            "discount_value": data["discount_value"],
            "min_order_amount": 0,
            "max_discount": None,
            "quantity": data.get("quantity"),
            "is_active": True,
            "expires_at": data.get("expires_at"),
        },
    )
    return voucher_data(voucher)


def list_vouchers(db: Session) -> dict:
    vouchers = repo_payment.get_vouchers(db).all()
    return {
        "data": [voucher_data(voucher) for voucher in vouchers],
    }
