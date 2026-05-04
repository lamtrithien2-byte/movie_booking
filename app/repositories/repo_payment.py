from sqlalchemy.orm import Session

from app.models.model_payment import Payment, Voucher


def create_payment(db: Session, data: dict):
    payment = Payment(**data)
    db.add(payment)
    db.flush()
    return payment


def get_payment_by_order_code(db: Session, order_code: int):
    return db.query(Payment).filter(Payment.order_code == order_code).first()


def get_payment_by_id(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_latest_payment_by_booking_id(db: Session, booking_id: int):
    return (
        db.query(Payment)
        .filter(Payment.booking_id == booking_id)
        .order_by(Payment.created_at.desc(), Payment.id.desc())
        .first()
    )


def get_voucher_by_code(db: Session, code: str):
    return db.query(Voucher).filter(Voucher.code == code).first()


def get_vouchers(db: Session):
    return db.query(Voucher).order_by(Voucher.created_at.desc(), Voucher.id.desc())


def get_pending_payments(db: Session, limit: int = 5):
    return (
        db.query(Payment)
        .filter(Payment.status == "pending", Payment.order_code.isnot(None))
        .order_by(Payment.created_at.asc(), Payment.id.asc())
        .limit(limit)
    )


def create_voucher(db: Session, data: dict):
    voucher = Voucher(**data)
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    return voucher
