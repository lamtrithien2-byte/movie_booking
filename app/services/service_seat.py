from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import repo_seat, repo_showtime


def row_name(index: int) -> str:
    name = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def all_seat_codes(total_rows: int, total_cols: int) -> set[str]:
    return {
        f"{row_name(row)}{col}"
        for row in range(total_rows)
        for col in range(1, total_cols + 1)
    }


def normalize_seats(seat_codes: list[str]) -> list[str]:
    return sorted({seat_code.strip().upper() for seat_code in seat_codes if seat_code.strip()})


def get_showtime_room(db: Session, showtime_id: int):
    showtime = repo_showtime.get_showtime_by_id(db, showtime_id)
    if showtime is None or not showtime.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")

    if showtime.room is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Showtime has no room")

    return showtime


def seat_map(db: Session, showtime_id: int, selected_seats: list[str] | None = None) -> dict:
    showtime = get_showtime_room(db, showtime_id)
    selected = set(normalize_seats(selected_seats or []))
    booked = {seat.seat_code for seat in repo_seat.get_booked_seats(db, showtime_id)}
    valid, message = validate_selected_seats(showtime, selected, booked)

    return {
        "showtime_id": showtime.id,
        "room": {
            "id": showtime.room.id,
            "name": showtime.room.name,
            "total_rows": showtime.room.total_rows,
            "total_cols": showtime.room.total_cols,
        },
        "is_valid": valid,
        "message": message,
        "seats": build_seats(showtime.room, selected, booked),
    }


def build_seats(room, selected: set[str], booked: set[str]) -> list[dict]:
    rows = []
    for row in range(room.total_rows):
        row_label = row_name(row)
        seats = []
        for col in range(1, room.total_cols + 1):
            seat_code = f"{row_label}{col}"
            status_text = "available"
            if seat_code in booked:
                status_text = "booked"
            elif seat_code in selected:
                status_text = "selected"

            seats.append({
                "code": seat_code,
                "row": row_label,
                "number": col,
                "status": status_text,
            })
        rows.append({
            "row": row_label,
            "seats": seats,
        })
    return rows


def validate_selected_seats(showtime, selected: set[str], booked: set[str]) -> tuple[bool, str]:
    room = showtime.room
    valid_codes = all_seat_codes(room.total_rows, room.total_cols)

    if not selected:
        return True, "OK"

    invalid_seats = selected - valid_codes
    if invalid_seats:
        return False, f"Invalid seats: {', '.join(sorted(invalid_seats))}"

    already_booked = selected & booked
    if already_booked:
        return False, f"Seats booked: {', '.join(sorted(already_booked))}"

    for row in range(room.total_rows):
        row_label = row_name(row)
        states = []
        for col in range(1, room.total_cols + 1):
            seat_code = f"{row_label}{col}"
            states.append(seat_code in booked or seat_code in selected)

        if has_single_empty_seat(states):
            return False, "cant leave a odd seat"

    return True, "OK"


def has_single_empty_seat(states: list[bool]) -> bool:
    empty_count = 0
    for occupied in states + [True]:
        if not occupied:
            empty_count += 1
            continue
        if empty_count == 1:
            return True
        empty_count = 0
    return False


def book_seats(db: Session, showtime_id: int, selected_seats: list[str]) -> dict:
    showtime = get_showtime_room(db, showtime_id)
    selected = set(normalize_seats(selected_seats))
    if not selected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please choose seats")

    booked = {seat.seat_code for seat in repo_seat.get_booked_seats(db, showtime_id)}
    valid, message = validate_selected_seats(showtime, selected, booked)

    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    try:
        repo_seat.create_booked_seats(db, showtime_id, sorted(selected))
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="seat were booked",
        ) from exc

    return seat_map(db, showtime_id)
