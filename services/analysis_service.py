from services.analysis_logic import SkinAnalyzer
from config.firebase_config import db
import uuid

class AnalysisService:
    """Service to analyze skin images and save results to Firestore."""
    def __init__(self):
        self.analyzer = SkinAnalyzer()

    def analyze_and_save(self, user_id, image_path):
        result = self.analyzer.analyze_image(image_path, user_id)
        data = result.to_dict()

        # Save to Firestore
        db.collection("SkinAnalysis").document(data["AnalysisID"]).set(data)
        return data