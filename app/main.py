from fastapi import FastAPI
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.cinemas import router as cinemas_router
from app.api.movies import router as movies_router
from app.api.roles import router as roles_router
from app.api.users import router as users_router
from app.db.db_database import engine

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(movies_router)
app.include_router(cinemas_router)

@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"message": "PostgreSQL connected successfully"}
