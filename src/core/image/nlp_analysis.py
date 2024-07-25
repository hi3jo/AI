import os
import base64
import io
from dotenv import load_dotenv
from fastapi import UploadFile
from typing import List
from openai import OpenAI

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 환경 변수에서 OpenAI API 키를 가져옵니다.
api_key = os.getenv('OPENAI_API_KEY')

# API 키로 OpenAI 클라이언트를 초기화합니다.
client = OpenAI(api_key=api_key)

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

async def analyze_text_from_image(files: List[UploadFile]) -> dict:
    results = []
    for file in files:
        contents = await file.read()
        base64_image = encode_image(io.BytesIO(contents))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """이 텍스트 이미지의 내용을 분석해주세요. 
                         다음 사항들을 포함해주세요:
                         - 제공된 텍스트를 분석하고 한국어로 요약하세요. 이모티콘이나 스티커는 무시하고 오직 텍스트만 분석해주세요.
                         - 대화에 성적인 내용이 포함되어 있는지 간단히 명시하세요. 구체적인 표현을 인용하지 마세요.
                         - 대화가 부적절한 관계로 보일 수 있는지 간략히 평가하세요.
                         - 중복된 내용의 응답을 하지마세요.
                        주의: 응답에서 성적인 표현을 직접 인용하지 마세요."""},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ],
                }
            ],
            max_tokens=500,
        )
        results.append({
            "analysis": response.choices[0].message.content
        })
    return {"results": results}