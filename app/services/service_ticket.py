from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import repo_booking

TICKET_DIR = Path(__file__).resolve().parents[1] / "tickets"


def ticket_path(booking_id: int) -> Path:
    return TICKET_DIR / f"ticket_BK{booking_id:06d}.pdf"


def ticket_lines(ticket: dict) -> list[str]:
    return [
        "MOVIE BOOKING TICKET",
        f"Ma ve: {ticket['ticket_code']}",
        "",
        f"Phim: {ticket['movie_title']}",
        f"The loai: {ticket['movie_type'] or ''}",
        f"Thoi luong: {ticket['movie_duration']} phut",
        "",
        f"Rap: {ticket['cinema_name']}",
        f"Dia chi: {ticket['cinema_address']}",
        f"Thanh pho: {ticket['cinema_city']}",
        f"Quan: {ticket['cinema_district'] or ''}",
        "",
        f"Ngay chieu: {ticket['show_date']}",
        f"Gio chieu: {ticket['show_time']}",
        "Thanh toan: PayOS",
        f"Voucher: {ticket.get('voucher_code') or ''}",
        f"Tien thanh toan: {ticket.get('final_amount') or 0}",
        f"Phong: {ticket['room_name'] or ''}",
        f"Ghe: {ticket['seats'] or ''}",
        f"So luong ghe: {ticket['total_seats']}",
        "",
    ]


def create_ticket_pdf(db: Session, booking_id: int) -> Path:
    ticket = repo_booking.get_booking_detail_by_id(db, booking_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay booking")

    path = ticket_path(booking_id)
    TICKET_DIR.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_pdf(ticket_lines(ticket)))
    return path


def build_pdf(lines: list[str]) -> bytes:
    content = ["BT", "/F1 16 Tf", "50 790 Td", "22 TL"]
    for index, line in enumerate(lines):
        if index == 1:
            content.append("/F1 11 Tf")
        content.append(f"({escape_pdf_text(line)}) Tj")
        content.append("T*")
    content.append("ET")

    stream = "\n".join(content).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    object_count = len(objects) + 1
    pdf.extend(f"xref\n0 {object_count}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())

    pdf.extend(f"trailer\n<< /Size {object_count} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode())
    return bytes(pdf)


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
