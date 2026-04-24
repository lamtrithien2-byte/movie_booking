from datetime import datetime, time

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.db.db_database import get_db
from app.services import service_payment, service_ticket
from app.services.service_auth import require_roles

router = APIRouter(tags=["payments"])


class CreatePaymentRequest(BaseModel):
    payment_method: str = Field(pattern="^(card|bank_transfer)$")
    voucher_code: str | None = None


class VoucherRequest(BaseModel):
    code: str = Field(min_length=3, max_length=50, examples=["SALE10"])
    discount_value: int = Field(gt=0, examples=[10])
    quantity: int | None = Field(default=None, gt=0)
    expires_at: str | None = Field(default=None, examples=["31/12/2026"])

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, value: str | None) -> str | None:
        if not value:
            return None
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError as exc:
            raise ValueError("expires_at must be dd/mm/yyyy, example: 31/12/2026") from exc
        return value

    def to_data(self) -> dict:
        data = self.model_dump()
        if self.expires_at:
            expire_date = datetime.strptime(self.expires_at, "%d/%m/%Y").date()
            data["expires_at"] = datetime.combine(expire_date, time.max)
        return data


class VoucherResponse(BaseModel):
    id: int
    code: str
    discount_value: int
    quantity: int | None
    used_count: int
    is_active: bool
    expires_at: datetime | None


@router.post("/bookings/{booking_id}/payments", status_code=status.HTTP_201_CREATED)
def create_payment(
    booking_id: int,
    body: CreatePaymentRequest,
    db: Session = Depends(get_db),
):
    return service_payment.create_payment(db, booking_id, body.model_dump())


@router.get("/bookings/{booking_id}/payments/ticket")
def download_ticket(booking_id: int, db: Session = Depends(get_db)):
    path = service_ticket.create_ticket_pdf(db, booking_id)
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=path.name,
    )


@router.get("/admin/vouchers")
def get_vouchers(
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_payment.list_vouchers(db)


@router.post("/admin/vouchers", status_code=status.HTTP_201_CREATED, response_model=VoucherResponse)
def create_voucher(
    body: VoucherRequest,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    return service_payment.create_voucher(db, body.to_data())
