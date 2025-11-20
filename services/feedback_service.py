import datetime
import uuid
from firebase_admin import firestore

# ==================================================
# FEEDBACK DATA MODEL
# ==================================================
class Feedback:
    """Model for user feedback on product recommendation or skin analysis results."""

    def __init__(self, user_id, category, reference_id, rating, comments=""):
        """
        :param user_id: ID of the user giving feedback
        :param category: 'Product' or 'Analysis'
        :param reference_id: The ID of the product or analysis being rated
        :param rating: Integer rating (1-5)
        :param comments: Optional text feedback
        """
        self.feedback_id = str(uuid.uuid4())
        self.user_id = user_id
        self.category = category
        self.reference_id = reference_id
        self.rating = rating
        self.comments = comments
        self.date = datetime.datetime.now().isoformat()

    def to_dict(self):
        return {
            "FeedbackID": self.feedback_id,
            "UserID": self.user_id,
            "Category": self.category,
            "ReferenceID": self.reference_id,
            "Rating": self.rating,
            "Comments": self.comments,
            "Date": self.date
        }


# ==================================================
# FEEDBACK SERVICE
# ==================================================
class FeedbackService:
    """Handles CRUD operations for user feedback."""
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("Feedback")

    # --------------------------------------------------
    def add_feedback(self, feedback: Feedback):
        """Add a new feedback entry."""
        self.collection.document(feedback.feedback_id).set(feedback.to_dict())
        return {"message": "Feedback added successfully", "FeedbackID": feedback.feedback_id}

    # --------------------------------------------------
    def get_feedback_by_user(self, user_id: str):
        """Retrieve all feedback given by a specific user."""
        docs = self.collection.where("UserID", "==", user_id).stream()
        feedback_list = [doc.to_dict() for doc in docs]
        return feedback_list if feedback_list else {"message": "No feedback found for this user."}

    # --------------------------------------------------
    def get_feedback_for_reference(self, reference_id: str):
        """Retrieve feedback for a particular product/analysis."""
        docs = self.collection.where("ReferenceID", "==", reference_id).stream()
        feedback_list = [doc.to_dict() for doc in docs]
        return feedback_list if feedback_list else {"message": "No feedback found for this reference."}

    # --------------------------------------------------
    def update_feedback(self, feedback_id: str, new_rating: int = None, new_comments: str = None):
        """Allow user to update their feedback."""
        doc_ref = self.collection.document(feedback_id)
        doc = doc_ref.get()
        if not doc.exists:
            return {"error": "Feedback not found."}

        updates = {}
        if new_rating is not None:
            updates["Rating"] = new_rating
        if new_comments is not None:
            updates["Comments"] = new_comments

        if updates:
            updates["Date"] = datetime.datetime.now().isoformat()
            doc_ref.update(updates)
            return {"message": "Feedback updated successfully."}
        else:
            return {"message": "No updates made."}

    # --------------------------------------------------
    def delete_feedback(self, feedback_id: str):
        """Delete a feedback record."""
        doc_ref = self.collection.document(feedback_id)
        if doc_ref.get().exists:
            doc_ref.delete()
            return {"message": "Feedback deleted successfully."}
        else:
            return {"error": "Feedback not found."}

