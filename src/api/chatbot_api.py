from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from src.core.chatbot import ask_chatgpt                # 모듈화한 함수 가져오기 : 경로를 모두 포함시킨다.

router = APIRouter()

class Question(BaseModel):
    question: str

@router.post("/asked")
async def ask(question: Question):
    
    print("클라이언트로부터 전달 된 질문 : ", question)
    
    # 1.질문 내용이 빈값인 채로 서버로 전달되었을 때.
    if not question.question:
        raise HTTPException(status_code=400, detail="No question provided")
    
    # 2.질문 내용을 챗GPT에게 전달.
    answer = ask_chatgpt(question.question)
    return {"answer": answer}