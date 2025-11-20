import cv2 
import dlib
import numpy as np
import uuid
import datetime
import os
import gdown
from config.firebase_config import db  


class SkinAnalysisResult:
    """Stores all computed skin analysis data."""
    def __init__(self, user_id, image_path):
        self.analysis_id = str(uuid.uuid4())
        self.user_id = user_id
        self.image_path = image_path
        self.analysis_date = datetime.datetime.now().isoformat()
        self.face_detected = False
        self.skin_tone = None
        self.skin_condition = None
        self.cr_mean = None
        self.cb_mean = None
        self.a_mean = None
        self.b_mean = None
        self.confidence_score = 0.0
        self.lighting_adjusted = True
        self.recommendations = []
        self.user_feedback = None
        self.notes = ""
        self.landmarks = []

    def to_dict(self):
        return {
            "AnalysisID": self.analysis_id,
            "UserID": self.user_id,
            "ImagePath": self.image_path,
            "AnalysisDate": self.analysis_date,
            "FaceDetected": self.face_detected,
            "SkinTone": self.skin_tone,
            "SkinCondition": self.skin_condition,
            "CrMean": self.cr_mean,
            "CbMean": self.cb_mean,
            "aMean": self.a_mean,
            "bMean": self.b_mean,
            "ConfidenceScore": self.confidence_score,
            "LightingAdjusted": self.lighting_adjusted,
            "Recommendations": self.recommendations,
            "UserFeedback": self.user_feedback,
            "Notes": self.notes,
            "Landmarks": self.landmarks
        }


class SkinAnalyzer:
    def __init__(self):

        # --- Google Drive Model Download ---
        drive_id = "1-HTqUcR9a76I5zrJk95ZrXD6dzH-jowL"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, "shape_predictor_68_face_landmarks.dat")
        url = f"https://drive.google.com/uc?id={drive_id}"

        # If model not exists → download
        if not os.path.exists(self.model_path):
            print("Downloading face landmark model from Google Drive...")
            gdown.download(url, self.model_path, quiet=False)
            print("Download complete!")

        # Load detector + predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.model_path)


    def _adjust_lighting(self, roi):
        ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        y = cv2.equalizeHist(y)
        adjusted = cv2.merge([y, cr, cb])
        return cv2.cvtColor(adjusted, cv2.COLOR_YCrCb2BGR)

    def _calculate_metrics(self, roi):
        ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
        lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
        _, cr, cb = cv2.split(ycrcb)
        l, a, b = cv2.split(lab)
        return np.mean(cr), np.mean(cb), np.mean(a), np.mean(b)

    def _classify_tone(self, cr, cb, a, b):
        tone = "Neutral"
        confidence = 0.6
        if cr > 150 and b > 140:
            tone, confidence = "Warm", min((cr - 145) / 40, 1.0)
        elif cr < 145 and cb > 120:
            tone, confidence = "Cool", min((150 - cr) / 40, 1.0)
        else:
            tone, confidence = "Neutral", 0.7
        return tone, round(confidence, 2)

    def _detect_condition(self, cr, cb, a, b):
        if a > 140 and b < 130:
            return "Oily"
        elif b > 150:
            return "Dry"
        else:
            return "Balanced"

    def _recommend_products(self, tone, condition):
        rules = {
            ("Warm", "Oily"): ["Oil-Free Moisturizer", "Matte Sunscreen"],
            ("Cool", "Dry"): ["Hydrating Cream", "Aloe Soothing Gel"],
            ("Neutral", "Balanced"): ["Gentle Cleanser", "Light Moisturizer"]
        }
        return rules.get((tone, condition), ["General Skincare Kit"])

    def analyze_image(self, image_path, user_id="UnknownUser"):
        result = SkinAnalysisResult(user_id, image_path)
        image = cv2.imread(image_path)

        if image is None:
            result.notes = "Image not found or unreadable."
            return result

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        if not faces:
            result.notes = "No face detected."
            return result

        face = faces[0]
        result.face_detected = True

        landmarks = self.predictor(gray, face)
        points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)]
        result.landmarks = [{"x": x, "y": y} for x, y in points]

        mask = np.zeros_like(image)
        cv2.fillConvexPoly(mask, np.array(points, dtype=np.int32), (255, 255, 255))
        skin_region = cv2.bitwise_and(image, mask)

        cx = face.left() + face.width() // 2
        cy = face.top() + face.height() // 2
        box_size = 40
        roi = skin_region[cy - box_size:cy + box_size, cx - box_size:cx + box_size]

        if roi.size == 0:
            result.notes = "ROI is empty or invalid."
            return result

        roi = self._adjust_lighting(roi)
        cr_mean, cb_mean, a_mean, b_mean = self._calculate_metrics(roi)

        result.cr_mean = round(float(cr_mean), 2)
        result.cb_mean = round(float(cb_mean), 2)
        result.a_mean = round(float(a_mean), 2)
        result.b_mean = round(float(b_mean), 2)

        tone, confidence = self._classify_tone(cr_mean, cb_mean, a_mean, b_mean)
        condition = self._detect_condition(cr_mean, cb_mean, a_mean, b_mean)

        result.skin_tone = tone
        result.skin_condition = condition
        result.confidence_score = confidence
        result.recommendations = self._recommend_products(tone, condition)
        result.notes = f"Tone: {tone}, Condition: {condition}, Confidence: {confidence}"

        return result
