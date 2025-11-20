import uuid
import datetime
import requests
from firebase_admin import firestore

# ==================================================
# PRODUCT RECOMMENDATION MODEL
# ==================================================
class Recommendation:
    """Model representing recommended skincare products for a user."""

    def __init__(self, user_id, skin_tone, skin_condition, source_analysis_id):
        self.recommendation_id = str(uuid.uuid4())
        self.user_id = user_id
        self.skin_tone = skin_tone
        self.skin_condition = skin_condition
        self.source_analysis_id = source_analysis_id
        self.date_generated = datetime.datetime.now().isoformat()
        self.products = []  # Product list fetched from rule-based logic or API

    def to_dict(self):
        return {
            "RecommendationID": self.recommendation_id,
            "UserID": self.user_id,
            "SkinTone": self.skin_tone,
            "SkinCondition": self.skin_condition,
            "SourceAnalysisID": self.source_analysis_id,
            "DateGenerated": self.date_generated,
            "Products": self.products
        }


# ==================================================
# RECOMMENDATION SERVICE CLASS
# ==================================================
class RecommendationService:
    """Handles generation, storage, and retrieval of skincare product recommendations."""
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("Recommendations")

    # --------------------------------------------------
    def generate_recommendations(self, user_id, skin_tone, skin_condition, analysis_id):
        """Generate product recommendations using both internal rules and external API calls."""

        rec = Recommendation(user_id, skin_tone, skin_condition, analysis_id)

        # --- Internal Rule-based Logic ---
        base_products = self._get_base_recommendations(skin_tone, skin_condition)

        # --- Fetch products dynamically from Shopee/Taobao (Optional) ---
        try:
            api_products = self._fetch_products_from_api(skin_tone, skin_condition)
        except Exception as e:
            api_products = [{"name": "Fallback Moisturizer", "source": "Local", "error": str(e)}]

        rec.products = base_products + api_products

        # --- Store in Firebase ---
        self.collection.document(rec.recommendation_id).set(rec.to_dict())

        return {"message": "Recommendations generated successfully.", "data": rec.to_dict()}

    # --------------------------------------------------
    def _get_base_recommendations(self, tone, condition):
        """Static fallback recommendations."""
        rules = {
            ("Warm", "Oily"): [
                {"name": "Oil-Free Cleanser", "type": "Cleanser"},
                {"name": "Matte Sunscreen SPF 50", "type": "Sunscreen"},
            ],
            ("Cool", "Dry"): [
                {"name": "Hydrating Cream", "type": "Moisturizer"},
                {"name": "Aloe Soothing Mask", "type": "Mask"},
            ],
            ("Neutral", "Balanced"): [
                {"name": "Gentle Cleanser", "type": "Cleanser"},
                {"name": "Light Moisturizer", "type": "Moisturizer"},
            ]
        }
        return rules.get((tone, condition), [{"name": "Basic Skincare Kit", "type": "Set"}])

    # --------------------------------------------------
    def _fetch_products_from_api(self, tone, condition):
        """
        Example external API call to Shopee/Taobao.
        Replace this with actual API endpoint and key if available.
        """
        query = f"{tone} {condition} skincare"
        print(f"[API Fetch] Searching external API for: {query}")

        # Example pseudo endpoint (replace with actual)
        url = f"https://api.shopeemock.com/search?q={query}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            # Simplify to top 3 products
            return [
                {"name": item["title"], "price": item.get("price", "N/A"), "source": "ShopeeMock"}
                for item in data.get("items", [])[:3]
            ]
        else:
            raise Exception(f"External API Error ({response.status_code})")

    # --------------------------------------------------
    def get_recommendations_by_user(self, user_id):
        """Retrieve all recommendations for a user."""
        docs = self.collection.where("UserID", "==", user_id).stream()
        results = [doc.to_dict() for doc in docs]
        return results if results else {"message": "No recommendations found for this user."}

    # --------------------------------------------------
    def get_recommendation_by_id(self, recommendation_id):
        """Retrieve a single recommendation by its ID."""
        doc_ref = self.collection.document(recommendation_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return {"error": "Recommendation not found."}

    # --------------------------------------------------
    def update_recommendation_feedback(self, recommendation_id, feedback_data):
        """Attach user feedback (e.g., satisfaction or product rating)."""
        doc_ref = self.collection.document(recommendation_id)
        if not doc_ref.get().exists:
            return {"error": "Recommendation not found."}

        update_data = {"Feedback": feedback_data, "UpdatedAt": datetime.datetime.now().isoformat()}
        doc_ref.update(update_data)
        return {"message": "Recommendation feedback updated successfully."}

