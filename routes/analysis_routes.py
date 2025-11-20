import os 
from fastapi import APIRouter, UploadFile, File, Form, HTTPException # Added HTTPException
from services.analysis_service import AnalysisService
import tempfile
import shutil 

router = APIRouter()

service = AnalysisService()

@router.post("/analyze", tags=["Analysis"])
async def analyze_skin(user_id: str = Form(..., description="The ID of the user submitting the image."), file: UploadFile = File(..., description="The skin image file.")):
    """
    Accepts an image file and a user ID, performs skin analysis, 
    saves the result to Firestore, and cleans up the temporary file.
    """
    temp_path = None
    try:
 
        suffix = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:

            contents = await file.read()
            temp.write(contents)
            temp_path = temp.name 

        result_data = service.analyze_and_save(user_id, temp_path)

        if not result_data.get("FaceDetected", True):
             raise HTTPException(
                status_code=400, 
                detail=f"Analysis failed: {result_data.get('Notes', 'No face detected or image invalid.')}"
             )

        return {"status": "success", "data": result_data}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Server Error during skin analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
        
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Cleaned up temporary file: {temp_path}")