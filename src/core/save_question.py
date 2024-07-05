import requests
import json

def connect_back(question):
    
    print("1. 백엔드 연결을 위한 메소드 호출 됨 : ", question)
    
    backend_url = 'http://localhost:8080/api/chatbot/ask'   # 백엔드 서버 URL
    ask         = question.question                         # 사용자의 질문
    userid      = question.userid                           # 사용자 아이디

    # 데이터를 JSON 형식으로 만듦
    data = {  'ask'    : ask 
            , 'userId' : userid}

    print("2. 벡엔드로 전달할 파라미터 :", data)
    # JSON 데이터를 HTTP POST 요청으로 백엔드 서버에 전송
    try:
        
        response = requests.post(backend_url, json=data, allow_redirects=False)

        # 응답 확인
        if response.status_code == 200:
            print('데이터 전송 성공')
            ask_id = response.json()
            print(f'응답 데이터: {ask_id}')
            return ask_id;
        else:
            print(f'데이터 전송 실패 - 응답 코드: {response.status_code}')
            print(f'응답 내용: {response.text}')

    except requests.exceptions.RequestException as e:
        print(f'데이터 전송 중 오류 발생: {e}')