from fastapi import FastAPI
import config.firebase_config
from routes import user_routes, feedback_routes, recommendation_routes, analysis_routes

app = FastAPI(title="SkinGloss Backend")

app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(feedback_routes.router, prefix="/feedback", tags=["Feedback"])
app.include_router(recommendation_routes.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(analysis_routes.router, prefix="/analysis", tags=["Analysis"])

@app.get("/")
def root():
    return {"message": "Welcome to SkinGloss Backend API"}
