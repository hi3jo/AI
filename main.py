from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.webtoon_api import router as webtoon_router
from src.api.data_upload_api import router as upload_router_v4
from src.api.chat_query_api import router as query_router_v4
from src.api.image_analysis_api import image_analysis_router
from src.api.text_image_analysis_api import text_image_analysis_router  # 새로운 라우터 임포트

app = FastAPI()

# 1. CORS 설정
# 1.1. 필요한 domain만 허용하도록 변경 가능
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
app.include_router(text_image_analysis_router, prefix="/api")  # 텍스트 이미지 분석 라우터 추가

@app.get("/")
async def root():
    return {"message": "Ai server start..."}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
