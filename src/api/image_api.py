from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from src.core.dalleImg import generate_and_display_comic                  # 모듈화한 함수 가져오기 : 경로를 모두 포함시킨다.

router = APIRouter()

class WebtoonPrompt(BaseModel):
    question: str  

# 기존 코드 prompt로 하면 422 에러가 남.
# 사연을 토대로 4컷 웹툰 생성 요청
@router.post("/generate-webtoon")
async def generate_webtoon_endpoint(question: WebtoonPrompt):
    
    print("화면에서 받아온 내용 뭘까 ", question.question)
    if not question.question:
        raise HTTPException(status_code=400, detail="No prompt provided")
    
    # 이미지 생성 및 base64 인코딩
    image_base64 = generate_and_display_comic(question.question)
    if not image_base64:
        raise HTTPException(status_code=500, detail="Failed to generate webtoon")
    
    return {"image": image_base64}