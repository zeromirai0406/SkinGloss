import firebase_admin
from firebase_admin import credentials, firestore, storage

if not firebase_admin._apps:
    cred = credentials.Certificate("skingloss-1d5bc-firebase-adminsdk-fbsvc-9e980c47ae")
    firebase_admin.initialize_app(cred, {
        "storageBucket": "skingloss-1d5bc.appspot.com"  
    })

# Firestore client
db = firestore.client()

# Storage client
bucket = storage.bucket()

