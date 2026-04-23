from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import repo_booking
from app.services.service_booking import booking_data

BASE_DIR = Path(__file__).resolve().parents[1]
TICKET_DIR = BASE_DIR / "tickets"


def ticket_path(booking_id: int) -> Path:
    return TICKET_DIR / f"ticket_BK{booking_id:06d}.pdf"


def create_ticket_pdf(db: Session, booking_id: int) -> Path:
    booking = repo_booking.get_booking_by_id(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay booking")

    ticket = booking_data(booking)
    movie = ticket["movie"]
    cinema = ticket["cinema"]
    room = ticket["room"]
    showtime = ticket["showtime"]

    lines = [
        "MOVIE BOOKING TICKET",
        f"Ma ve: {ticket['ticket_code']}",
        f"Trang thai: {ticket['status']}",
        "",
        f"Phim: {movie['title']}",
        f"The loai: {movie['type'] or ''}",
        f"Thoi luong: {movie['duration']} phut",
        "",
        f"Rap: {cinema['name']}",
        f"Dia chi: {cinema['address']}",
        f"Thanh pho: {cinema['city']}",
        f"Quan: {cinema['district'] or ''}",
        "",
        f"Ngay chieu: {showtime['date']}",
        f"Gio chieu: {showtime['time']}",
        f"Phong: {room['name'] if room else ''}",
        f"Ghe: {', '.join(ticket['seats'])}",
        f"So luong ghe: {ticket['total_seats']}",
        "",
    ]

    TICKET_DIR.mkdir(parents=True, exist_ok=True)
    path = ticket_path(booking_id)
    path.write_bytes(build_pdf(lines))
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
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())

    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode()
    )
    return bytes(pdf)


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
