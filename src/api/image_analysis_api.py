from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from src.core.image.imageanalysis import analyze_image

router = APIRouter()

@router.post("/analysis-image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        analysis_result = analyze_image(file)
        return JSONResponse(content=analysis_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# image_upload_router 정의
image_analysis_router = router
