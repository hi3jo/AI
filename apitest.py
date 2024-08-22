import logging
import os
from dotenv import load_dotenv
import json
import requests
import time
import psutil # 메모리 사용량, CPU 사용량 확인

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

# Hugging Face API 토큰 설정
API_TOKEN = os.getenv('API_TOKEN')

# API 헤더 설정
headers = {"Authorization": f"Bearer {API_TOKEN}"}
# 임베딩 모델
API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
#API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-mpnet-base-v2"
# 채팅질문-답변 모델
# API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"

# 현재 시스템의 메모리와 CPU 사용량을 로그에 기록하는 함수
def log_system_resources():
    process = psutil.Process(os.getpid())  # 현재 프로세스의 정보 가져오기
    mem_info = process.memory_info()  # 현재 프로세스의 메모리 사용량 정보 가져오기
    cpu_usage = psutil.cpu_percent(interval=1)  # 1초간의 CPU 사용량 계산
    
    # 메모리 사용량과 CPU 사용량을 로그로 출력
    logger.info(f"Memory Usage: {mem_info.rss / 1024 ** 2:.2f} MB")  # RSS 메모리 사용량 MB 단위로 기록
    logger.info(f"CPU Usage: {cpu_usage}%")  # CPU 사용량 기록


# def query(payload):
#     data = json.dumps(payload)
#     response = requests.request("POST", API_URL, headers=headers, data=data)
#     return json.loads(response.content.decode("utf-8"))

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    # 시스템 리소스 상태 확인을 위한 로그 기록
    log_system_resources()
    return response.json()

# 재시도 로직을 구현
# def retry_query(payload, retries=3, delay=10):
#     for attempt in range(retries):
#         data = query(payload)
#         if "error" not in data:
#             return data
#         print(f"Retrying... ({attempt + 1}/{retries})")
#         time.sleep(delay)
#     return {"error": "Model loading timed out."}

# 채팅 질문-답변
# data = query(
#     {
#         "inputs": {
#             "question": "What's my name?",
#             "context": "My name is Clara and I live in Berkeley.",
#         }
#     }
# )

# 임베딩
data = query(
    {
        "inputs": {
            "source_sentence": "That is a happy person",
            "sentences": ["That is a happy dog", "That is a very happy person", "Today is a sunny day"],
        }
    }
)

print(data)