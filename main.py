from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.chatbot_api import router as chatbot_router

app = FastAPI()

# 1.CORS 설정
# 1.1.필요한 도메인만 허용하도록 변경 가능
app.add_middleware(
      CORSMiddleware
    , allow_origins=["*"]       
    , allow_credentials=True
    , allow_methods=["*"]
    , allow_headers=["*"]
)

app.include_router(chatbot_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)