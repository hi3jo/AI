import warnings
from fastapi import APIRouter, HTTPException, FastAPI
import logging
from src.core.chatbot.dalle2_image_generator import generate_images

# 경고 메시지 무시
warnings.filterwarnings("ignore", category=FutureWarning)

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 애플리케이션 초기화
app = FastAPI()

# 쿼리 라우터 정의
router = APIRouter()

@router.get("/chat-images/")
async def get_images():
    try:
        image_urls = generate_images()
        return {"image_urls": image_urls}
    except Exception as e:
        logger.error(f"이미지 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="이미지 생성 중 오류가 발생했습니다.")

# query_router 정의
chat_img_router = router

