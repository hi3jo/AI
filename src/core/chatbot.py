from dotenv import load_dotenv
from src.database.chatDB.select_data import search_vectorstore
import openai
import os

# .env 파일의 환경 변수를 로드합니다.
# OpenAI API 키 설정
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def ask_chatgpt(question: str) -> str:
    
    # question = '임신했는데 남편이 양육비 안줌 관련 판례일련번호'
    print("3.chatbot.py의 ask_chatgpt 함수로 전달 된 질문 : ", question)
    results = search_vectorstore(question)
    
    # print("4. vectorDB 다녀온 결과물 : ", results)
    
    if results is None or len(results['documents']) == 0:
        return "검색 결과를 찾을 수 없습니다."

    # 검색 결과에서 첫 번째 문서를 사용합니다.
    relevant_document = results['documents'][0]
    # print("5.relevant_document : ", relevant_document)

    # 문서를 하나의 문자열로 변환
    relevant_document_str = "\n".join(relevant_document)
    # print("relevant_document_str : ", relevant_document_str)
    
    # GPT에게 전달할 메시지 생성
    messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": f"The user asked: {question}\n\nHere are some similar documents:\n" + relevant_document_str},
    {"role": "assistant", "content": "Based on the above documents, provide a natural and informative response to the user's question in Korean.\n\n"}
]

    # ChatCompletion API 호출
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    print("")
    print("")
    print("-------------------------------------------------------------")
    print("화면으로 전달할 답변 데이터 :", response.choices[0].message['content'].strip())
    # GPT가 생성한 응답 반환
    return response.choices[0].message['content'].strip()\
       
if __name__ == '__main__':
    ask_chatgpt('ddd')        