from dotenv import load_dotenv
from src.database.chatDB.select_data import search_vectorstore  # 필요한 함수 가져오기
import openai
import os

# .env 파일의 환경 변수를 로드합니다.
# OpenAI API 키 설정
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def ask_chatgpt(question: str) -> str:
    
    print("chatbot.py의 ask_chatgpt : ", question)
    results = search_vectorstore(question)
    print("DB 다녀옴? : ", results)
    if results is None or len(results['documents']) == 0:
        return "검색 결과를 찾을 수 없습니다."
    
    # 검색 결과에서 첫 번째 문서를 사용합니다.
    relevant_document = results['documents'][0]
    print("relevant_document : ", relevant_document)
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