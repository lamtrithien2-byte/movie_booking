import os
import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import repo_booking, repo_payment, repo_seat

DEFAULT_TICKET_PRICE = int(os.getenv("DEFAULT_TICKET_PRICE", "90000"))
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
PAYOS_CLIENT_ID = os.getenv("PAYOS_CLIENT_ID")
PAYOS_API_KEY = os.getenv("PAYOS_API_KEY")
PAYOS_CHECKSUM_KEY = os.getenv("PAYOS_CHECKSUM_KEY")
PAYOS_CREATE_URL = "https://api-merchant.payos.vn/v2/payment-requests"


def payos_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "User-Agent": "movie-booking-fastapi/1.0",
        "x-client-id": PAYOS_CLIENT_ID or "",
        "x-api-key": PAYOS_API_KEY or "",
    }


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
        "order_code": payment.order_code,
        "checkout_url": payment.checkout_url,
        "qr_code": payment.qr_code,
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


def sign_data(data: dict, keys: list[str] | None = None) -> str:
    if not PAYOS_CHECKSUM_KEY:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Thieu PAYOS_CHECKSUM_KEY")

    keys = keys or sorted(data)
    raw_data = "&".join(f"{key}={data[key]}" for key in keys)
    return hmac.new(PAYOS_CHECKSUM_KEY.encode(), raw_data.encode(), hashlib.sha256).hexdigest()


def request_payos(url: str, method: str, data: dict | None = None) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data is not None else None,
        headers=payos_headers(),
        method=method,
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        message = exc.read().decode(errors="ignore")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Loi PayOS: {message}") from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Khong ket noi duoc PayOS: {exc.reason}") from exc


def get_payos_payment(order_code: int) -> dict:
    return request_payos(f"{PAYOS_CREATE_URL}/{order_code}", "GET")


def create_payos_link(payment) -> dict:
    if not PAYOS_CLIENT_ID or not PAYOS_API_KEY:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Thieu cau hinh PayOS")

    flow_url = f"{APP_BASE_URL}/flow-test?booking_id={payment.booking_id}"
    payment_data = {
        "amount": payment.final_amount,
        "cancelUrl": flow_url,
        "description": f"BOOKING{payment.booking_id}",
        "orderCode": payment.order_code,
        "returnUrl": flow_url,
    }
    payment_data["signature"] = sign_data(
        payment_data,
        ["amount", "cancelUrl", "description", "orderCode", "returnUrl"],
    )

    result = request_payos(PAYOS_CREATE_URL, "POST", payment_data)

    if result.get("code") != "00":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("desc", "Loi PayOS"))

    return result["data"]


def create_order_code(booking_id: int) -> int:
    return int(time.time() * 1000) + booking_id


def create_payment(db: Session, booking_id: int, data: dict) -> dict:
    booking = get_booking_for_payment(db, booking_id)
    seat_codes = pending_seat_codes(booking)
    amount = len(seat_codes) * DEFAULT_TICKET_PRICE
    voucher = get_valid_voucher(db, data.get("voucher_code"), amount)
    discount = discount_amount(amount, voucher)
    final_amount = amount - discount

    return create_payos_payment(db, booking, amount, discount, final_amount, voucher)


def get_latest_payment(db: Session, booking_id: int) -> dict:
    payment = repo_payment.get_latest_payment_by_booking_id(db, booking_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chua co payment")
    sync_payos_payment(db, payment)
    return payment_data(payment)


def payment_payload(booking_id: int, method: str, amount: int, discount: int, final_amount: int, voucher) -> dict:
    return {
        "booking_id": booking_id,
        "method": method,
        "status": "pending",
        "original_amount": amount,
        "discount_amount": discount,
        "final_amount": final_amount,
        "voucher_code": voucher.code if voucher else None,
    }


def create_payos_payment(db: Session, booking, amount: int, discount: int, final_amount: int, voucher) -> dict:
    payment = repo_payment.create_payment(
        db,
        {
            **payment_payload(booking.id, "payos", amount, discount, final_amount, voucher),
            "order_code": create_order_code(booking.id),
        },
    )
    payos_data = create_payos_link(payment)
    payment.checkout_url = payos_data.get("checkoutUrl")
    payment.qr_code = payos_data.get("qrCode")
    db.commit()
    db.refresh(payment)
    return payment_data(payment)


def complete_payment(db: Session, payment, booking, seat_codes: list[str], voucher=None) -> dict:
    try:
        payment.paid_at = datetime.now(timezone.utc)
        payment.status = "paid"
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


def sync_payos_payment(db: Session, payment) -> None:
    if payment.status == "paid" or not payment.order_code:
        return

    result = get_payos_payment(payment.order_code)
    payos_data = result.get("data") or {}
    is_paid = payos_data.get("status") == "PAID" or payos_data.get("amountPaid", 0) >= payment.final_amount
    if not is_paid:
        return

    booking = repo_booking.get_booking_by_id(db, payment.booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay booking")

    voucher = repo_payment.get_voucher_by_code(db, payment.voucher_code) if payment.voucher_code else None
    complete_payment(db, payment, booking, pending_seat_codes(booking), voucher)


def verify_payos_webhook(body: dict) -> dict:
    data = body.get("data")
    signature = body.get("signature")
    if not isinstance(data, dict) or not signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Webhook PayOS khong hop le")

    if not hmac.compare_digest(sign_data(data), signature):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chu ky PayOS khong hop le")

    return data


def handle_payos_webhook(db: Session, body: dict) -> dict:
    data = verify_payos_webhook(body)
    if data.get("code") != "00":
        return {"success": True}

    payment = repo_payment.get_payment_by_order_code(db, int(data["orderCode"]))
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay payment")
    if payment.status == "paid":
        return {"success": True}

    booking = repo_booking.get_booking_by_id(db, payment.booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay booking")

    voucher = repo_payment.get_voucher_by_code(db, payment.voucher_code) if payment.voucher_code else None
    complete_payment(db, payment, booking, pending_seat_codes(booking), voucher)
    return {"success": True}


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
