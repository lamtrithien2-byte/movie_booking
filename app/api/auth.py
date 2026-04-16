from fastapi import APIRouter

router = APIRouter(prefix = "/auth")

auth=[]

@router.get("/")
def home():
    return {"trang chu"}

@router.get("/login")
def register():
    return {"vui long dang nhap"}