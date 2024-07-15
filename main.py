from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.webtoon_api import router as webtoon_router
from src.api.data_upload_api import router as upload_router_v4
from src.api.chat_query_api import router as query_router_v4

app = FastAPI()

# 1.CORS 설정
# 1.1.필요한 domain만 허용하도록 변경 가능
app.add_middleware(
      CORSMiddleware
    , allow_origins=["*"]       
    , allow_credentials=True
    , allow_methods=["*"]
    , allow_headers=["*"]
)

app.include_router(webtoon_router, prefix="/api")
app.include_router(upload_router_v4, prefix="/api") # VDB저장
app.include_router(query_router_v4, prefix="/api") # VDB저장

@app.get("/")
async def root():
    return {"message": "Ai server start..."}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)