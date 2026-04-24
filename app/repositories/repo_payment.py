from sqlalchemy.orm import Session

from app.models.model_payment import Payment, Voucher


def create_payment(db: Session, data: dict):
    payment = Payment(**data)
    db.add(payment)
    db.flush()
    return payment


def get_voucher_by_code(db: Session, code: str):
    return db.query(Voucher).filter(Voucher.code == code).first()


def get_vouchers(db: Session):
    return db.query(Voucher).order_by(Voucher.created_at.desc(), Voucher.id.desc())


def create_voucher(db: Session, data: dict):
    voucher = Voucher(**data)
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    return voucher
