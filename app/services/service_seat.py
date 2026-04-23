import time

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import repo_booking, repo_seat, repo_showtime

SELECT_EXPIRE_SECONDS = 300
selected_cache: dict[int, tuple[set[str], float]] = {}


def row_name(index: int) -> str:
    name = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def normalize_seats(seats: list[str]) -> set[str]:
    return {seat.strip().upper() for seat in seats if seat.strip()}


def save_selected(showtime_id: int, seats: set[str]) -> None:
    selected_cache[showtime_id] = (seats, time.time() + SELECT_EXPIRE_SECONDS)


def get_selected(showtime_id: int) -> set[str]:
    data = selected_cache.get(showtime_id)
    if data is None:
        return set()

    seats, expired_at = data
    if expired_at < time.time():
        clear_selected(showtime_id)
        return set()

    return seats


def clear_selected(showtime_id: int) -> None:
    selected_cache.pop(showtime_id, None)


def get_showtime(db: Session, showtime_id: int):
    showtime = repo_showtime.get_showtime_by_id(db, showtime_id)
    if showtime is None or not showtime.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay suat chieu")
    if showtime.room is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Suat chieu chua co phong")
    return showtime


def booked_codes(db: Session, showtime_id: int) -> set[str]:
    return {seat.seat_code for seat in repo_seat.get_booked_seats(db, showtime_id)}


def valid_codes(room) -> set[str]:
    return {
        f"{row_name(row)}{col}"
        for row in range(room.total_rows)
        for col in range(1, room.total_cols + 1)
    }


def get_seats(db: Session, showtime_id: int, selected_seats: list[str] | None = None) -> dict:
    showtime = get_showtime(db, showtime_id)
    selected = (
        get_selected(showtime_id)
        if selected_seats is None
        else normalize_seats(selected_seats)
    )
    booked = booked_codes(db, showtime_id)
    is_valid, message = validate_seats(showtime.room, selected, booked)
    total = showtime.room.total_rows * showtime.room.total_cols

    return {
        "showtime_id": showtime.id,
        "room": {
            "id": showtime.room.id,
            "name": showtime.room.name,
            "total_rows": showtime.room.total_rows,
            "total_cols": showtime.room.total_cols,
        },
        "total_seats": total,
        "booked_seats": len(booked),
        "available_seats": total - len(booked),
        "is_valid": is_valid,
        "message": message,
        "seats": build_seats(showtime.room, selected, booked),
    }


def select_seats(db: Session, showtime_id: int, selected_seats: list[str]) -> dict:
    result = get_seats(db, showtime_id, selected_seats)
    if result["is_valid"]:
        save_selected(showtime_id, normalize_seats(selected_seats))
    else:
        clear_selected(showtime_id)
    return result


def build_seats(room, selected: set[str], booked: set[str]) -> list[dict]:
    rows = []
    for row in range(room.total_rows):
        row_label = row_name(row)
        seats = []
        for col in range(1, room.total_cols + 1):
            code = f"{row_label}{col}"
            seats.append({
                "code": code,
                "row": row_label,
                "number": col,
                "status": seat_status(code, selected, booked),
            })

        rows.append({
            "row": row_label,
            "seats": seats,
        })
    return rows


def seat_status(code: str, selected: set[str], booked: set[str]) -> str:
    if code in booked:
        return "booked"
    if code in selected:
        return "selected"
    return "available"


def validate_seats(room, selected: set[str], booked: set[str]) -> tuple[bool, str]:
    if not selected:
        return True, "OK"

    invalid = selected - valid_codes(room)
    if invalid:
        return False, f"Ghe khong hop le: {', '.join(sorted(invalid))}"

    already_booked = selected & booked
    if already_booked:
        return False, f"Ghe da duoc dat: {', '.join(sorted(already_booked))}"

    for row in range(room.total_rows):
        row_label = row_name(row)
        occupied = []
        for col in range(1, room.total_cols + 1):
            code = f"{row_label}{col}"
            occupied.append(code in selected or code in booked)

        message = single_empty_seat_error(row_label, occupied)
        if message:
            return False, message

    return True, "OK"


def single_empty_seat_error(row_label: str, occupied: list[bool]) -> str | None:
    last_index = len(occupied) - 1
    for index, is_occupied in enumerate(occupied):
        if is_occupied:
            continue

        left_blocked = index == 0 or occupied[index - 1]
        right_blocked = index == last_index or occupied[index + 1]
        if not (left_blocked and right_blocked):
            continue

        seat_code = f"{row_label}{index + 1}"
        if index == 0:
            return f"Khong duoc de trong 1 ghe sat ben trai: {seat_code}"
        if index == last_index:
            return f"Khong duoc de trong 1 ghe sat ben phai: {seat_code}"
        return f"Khong duoc de trong 1 ghe o giua: {seat_code}"

    return None


def book_seats(db: Session, showtime_id: int, selected_seats: list[str]) -> dict:
    showtime = get_showtime(db, showtime_id)
    selected = normalize_seats(selected_seats)
    if not selected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui long chon ghe")

    booked = booked_codes(db, showtime_id)
    already_booked = selected & booked
    if already_booked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ghe da duoc dat: {', '.join(sorted(already_booked))}",
        )

    if selected != get_selected(showtime_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui long chon ghe truoc khi dat hoac ghe da het thoi gian giu",
        )

    is_valid, message = validate_seats(showtime.room, selected, booked)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    try:
        booking = repo_booking.create_booking(db, showtime_id)
        repo_seat.create_booked_seats(db, showtime_id, sorted(selected), booking.id)
        db.commit()
        db.refresh(booking)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mot vai ghe da duoc dat") from exc

    clear_selected(showtime_id)
    result = get_seats(db, showtime_id)
    result["booking_id"] = booking.id
    return result
