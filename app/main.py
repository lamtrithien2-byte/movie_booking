from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.cinemas import router as cinemas_router
from app.api.movies import router as movies_router
from app.api.roles import router as roles_router
from app.api.rooms import router as rooms_router
from app.api.seats import router as seats_router
from app.api.showtimes import router as showtimes_router
from app.api.users import router as users_router
from app.db.db_database import engine

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(movies_router)
app.include_router(cinemas_router)
app.include_router(showtimes_router)
app.include_router(rooms_router)
app.include_router(seats_router)

BASE_DIR = Path(__file__).resolve().parent


@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"message": "PostgreSQL connected successfully"}


@app.get("/flow-test")
def flow_test():
    return FileResponse(BASE_DIR / "flow_test.html")
