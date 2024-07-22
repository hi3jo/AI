# 5 API 라우터 모듈
# FastAPI를 사용하여 파일 업로드 엔드포인트를 정의

from fastapi import APIRouter, UploadFile, File
import shutil
import os

# 공통 설정 임포트
from src.core.data_upload.config import logger
from src.core.data_upload.data_processing import load_csv
from src.core.data_upload.embedding import embed_and_store_documents

# CSV 파일 업로드 라우터 정의
router = APIRouter()

@router.post("/upload-v4/")
async def upload_csv(file: UploadFile = File(...)):
    # 파일 저장 경로 설정
    data_dir = "./data"  # data 디렉터리 경로 설정
    if not os.path.exists(data_dir):  # data 디렉터리가 존재하지 않으면
        os.makedirs(data_dir)  # data 디렉터리 생성
    
    # 파일을 data 디렉터리에 저장하도록 파일 경로 설정
    file_location = os.path.join(data_dir, file.filename)  # 올바른 상대 경로 사용
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)  # 파일 저장

    # CSV 파일 로드
    docs = load_csv(file_location)
    if docs is None:
        return {"message": "CSV 파일 로드 실패"}

    result = embed_and_store_documents(docs)
    return result

# upload_router 정의
upload_router_v4 = router