from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from src.core.webtoon.dalle3_ai import generate_webtoon
from src.core.webtoon.dalle3_complex_ai import generate_webtoon_copy

router = APIRouter()

class WebtoonPrompt(BaseModel):
    story: str  

# 1.사연을 토대로 4컷 웹툰 생성 요청
@router.post("/generate-webtoon")
async def generate_webtoon_endpoint(story: WebtoonPrompt):
    
    #print("1.webtoon_api.py : 화면으로부터 전달받은 스토리 : ", story.story)
    # 1.Client로부터 전달 된 사연이 빈 값인지 확인
    if not story.story:
        raise HTTPException(status_code=400, detail="No prompt provided")
    
    # 2. OpenAI가 제공하는 DALL-E 3 를 이용하여 4컷 웹툰을 생성하고 base64 인코딩 처리 함.
    webtoon_image_base64 = generate_webtoon_copy(story.story)
    if not webtoon_image_base64:
        raise HTTPException(status_code=500, detail="Failed to generate webtoon")
    
    # 3.Client로 인코딩 처리된 웹툰 이미지 전달
    return {"webtoon": webtoon_image_base64}