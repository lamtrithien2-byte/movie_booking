from fastapi import APIRouter

router = APIRouter(prefix="/booking")

bookings = []


@router.get("/")
def booking_home():
    return {"message": "booking api"}


@router.get("/create")
def create_booking(name: str, movie: str):
    booking = {
        "name": name,
        "movie": movie,
    }
    bookings.append(booking)
    return {"booking": booking}


@router.get("/list")
def list_booking():
    return {"bookings": bookings}
