from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.webtoon_api import router as webtoon_router
from src.api.data_upload_api import router as upload_router_v4
from src.api.chat_query_api import router as query_router_v4
from src.api.image_analysis_api import image_analysis_router  # 추가된 라우터 임포트
from src.api.chat_dalle2_api import chat_img_router  # 채팅 이미지 생성

app = FastAPI()

# 1.CORS 설정
# 1.1.필요한 domain만 허용하도록 변경 가능
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(webtoon_router, prefix="/api")
app.include_router(upload_router_v4, prefix="/api")  # VDB 저장
app.include_router(query_router_v4, prefix="/api")   # VDB 저장
app.include_router(image_analysis_router, prefix="/api")  # 이미지 업로드 라우터 추가
app.include_router(chat_img_router, prefix="/api")  # 채팅 이미지 생성


@app.get("/")
async def root():
    return {"message": "Ai server start..."}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
