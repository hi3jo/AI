# 5 API 라우터 모듈
# FastAPI를 사용하여 파일 업로드 엔드포인트를 정의

from fastapi import APIRouter, UploadFile, File
import shutil
import os
# import fitz  # PyMuPDF를 이용한 PDF 처리

# 공통 설정 임포트
from src.core.data_upload.config import logger
from src.core.data_upload.data_processing import load_csv #load_pdf
from src.core.data_upload.embedding import embed_and_store_documents

# PDF 파일을 텍스트로 변환하는 함수
# def pdf_to_text(file_path):
#     try:
#         doc = fitz.open(file_path)
#         text = ""
#         for page in doc:
#             text += page.get_text()
#         if not text:
#             raise ValueError("텍스트를 추출할 수 없습니다.")
#         return text
#     except Exception as e:
#         logger.error(f"PDF 처리 중 오류 발생: {e}")
#         return None

# CSV 파일과 PDF 파일 업로드 라우터 정의
router = APIRouter()

@router.post("/upload-v4/")
async def upload_file(file: UploadFile = File(...)):
    # 파일 저장 경로 설정
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    file_location = os.path.join(data_dir, file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # 파일 확장자 확인
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension == ".csv":
        docs = load_csv(file_location)
        if docs is None:
            return {"message": "CSV 파일 로드 실패"}

    # elif file_extension == ".pdf":
    #     docs = load_pdf(file_location)  # load_pdf 함수가 직접 PDF 파일을 로드하고 청크로 분할
    #     if docs is None:
    #         return {"message": "PDF 파일 로드 실패"}

    else:
        return {"message": "지원되지 않는 파일 형식입니다"}

    # 문서 임베딩 및 저장
    result = embed_and_store_documents(docs)
    return result

# upload_router 정의
upload_router_v4 = router


