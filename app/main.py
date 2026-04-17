from fastapi import FastAPI
from sqlalchemy import text

from app.api.user.user_auth import router as auth_router
from app.db.db_database import engine

app = FastAPI()

app.include_router(auth_router)

@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"message": "PostgreSQL connected successfully"}
