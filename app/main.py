from fastapi import FastAPI

from app.api.booking import router as booking_router
from app.api.auth import router as auth_router

app = FastAPI()
app.include_router(booking_router)
app.include_router(auth_router)
