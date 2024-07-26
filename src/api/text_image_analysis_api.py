from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from src.core.image.text_image_analysis import analyze_text_from_images

router = APIRouter()

@router.post("/analysis-text/")
async def upload_text_image(files: List[UploadFile] = File(...)):
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files are allowed.")
    
    try:
        analysis_result = await analyze_text_from_images(files)
        return JSONResponse(content=analysis_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# text_image_analysis_router 정의
text_image_analysis_router = router