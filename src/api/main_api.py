from fastapi import APIRouter
from src.api.chatbot_api import router as chatbot_router
from src.api.webtoon_api import router as webtoon_router

router = APIRouter()

# Include the chatbot router with its endpoints
router.include_router(chatbot_router, prefix="/asked")

# Include the webtoon router with its endpoints
router.include_router(webtoon_router, prefix="/generate-webtoon")