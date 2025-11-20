from fastapi import APIRouter
from services.recommendation_service import RecommendationService

router = APIRouter()
service = RecommendationService()

@router.post("/")
def generate_recommendation(data: dict):
    return service.generate_recommendations(
        user_id=data["user_id"],
        skin_tone=data["skin_tone"],
        skin_condition=data["skin_condition"],
        analysis_id=data["analysis_id"]
    )

@router.get("/user/{user_id}")
def get_user_recommendations(user_id: str):
    return service.get_recommendations_by_user(user_id)

@router.get("/{recommendation_id}")
def get_recommendation_by_id(recommendation_id: str):
    return service.get_recommendation_by_id(recommendation_id)

@router.put("/{recommendation_id}/feedback")
def update_feedback(recommendation_id: str, feedback: dict):
    return service.update_recommendation_feedback(recommendation_id, feedback)
