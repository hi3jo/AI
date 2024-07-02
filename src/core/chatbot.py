from dotenv import load_dotenv
from src.database.chatDB.select_data import search_vectorstore
import openai
import os

# .env 파일의 환경 변수를 로드합니다.
# OpenAI API 키 설정
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def ask_chatgpt(question: str) -> str:
    
    print("3.chatbot.py의 ask_chatgpt 함수로 전달 된 질문 : ", question)
    results = search_vectorstore(question)
    
    print("4. vectorDB 다녀온 결과물 : ", results)
    
    if results is None or len(results['documents']) == 0:
        return "검색 결과를 찾을 수 없습니다."
    
    # 검색 결과에서 첫 번째 문서를 사용합니다.
    relevant_document = results['documents'][0]
    print("5.relevant_document : ", relevant_document)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            # 여기 부분이 prompt
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
            {"role": "assistant", "content": f"Related document: {relevant_document}"}
        ]
    )
    return response.choices[0].message['content'].strip()