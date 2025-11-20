from fastapi import APIRouter
from services.feedback_service import FeedbackService, Feedback

router = APIRouter()
feedback_service = FeedbackService()

@router.post("/")
def add_feedback(data: dict):
    feedback = Feedback(
        user_id=data["user_id"],
        category=data["category"],
        reference_id=data["reference_id"],
        rating=data["rating"],
        comments=data.get("comments", "")
    )
    return feedback_service.add_feedback(feedback)

@router.get("/user/{user_id}")
def get_user_feedback(user_id: str):
    return feedback_service.get_feedback_by_user(user_id)

@router.get("/reference/{reference_id}")
def get_reference_feedback(reference_id: str):
    return feedback_service.get_feedback_for_reference(reference_id)

@router.put("/{feedback_id}")
def update_feedback(feedback_id: str, new_data: dict):
    return feedback_service.update_feedback(
        feedback_id,
        new_rating=new_data.get("rating"),
        new_comments=new_data.get("comments")
    )

@router.delete("/{feedback_id}")
def delete_feedback(feedback_id: str):
    return feedback_service.delete_feedback(feedback_id)
