from fastapi import APIRouter

router = APIRouter()

@router.get("/{user_id}")
def get_user_profile(user_id: str):
    # FirebaseAuth validation later
    return {"user_id": user_id, "name": "Demo User", "status": "Active"}
