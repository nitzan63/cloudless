from fastapi import APIRouter, HTTPException, Body
from services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.post("/register")
def register(username: str = Body(...), password: str = Body(...), type: str = Body(...)):
    try:
        user_id = user_service.create_user(username, password, type)
        return {"status": "success", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{username}")
def get_user(username: str):
    user = user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user 