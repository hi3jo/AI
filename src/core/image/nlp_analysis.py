import os
import base64
import io
import json
from dotenv import load_dotenv
from fastapi import UploadFile
from typing import List
import openai

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 환경 변수에서 OpenAI API 키를 가져옵니다.
api_key = os.getenv('OPENAI_API_KEY')

# API 키를 설정합니다.
client = openai.OpenAI(api_key=api_key)

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
                        {"type": "text", "text": """
                            # 출력 형식
                            {
                                "대화내용": "대화 내용에 대한 요약을 하나의 연결된 문단으로 작성",
                                "성적표현": true 또는 false,
                                "부적절관계": true 또는 false
                            }
                            # 작업
                            - 최종 목표는 대화(메세지)내용을 분석하고 요약하는 것입니다.
                            - 이를 위해 단계별로 생각해 봅시다.
                            
                            ## 1단계
                            - 텍스트(메세지)이미지에서 '성적인' 내용과 '부적절한' 관계의 여부를 검토하세요.
                            - 성적인 내용이 있다면 '성적표현'을 true로, 없다면 false로 설정하세요.
                            - 부적절한 관계의 가능성이 있다면 '부적절관계'를 true로, 없다면 false로 설정하세요.
                            
                            ## 2단계
                            - 텍스트(메세지)이미지의 대화 내용을 1단계를 토대로 분석 후 요약하세요.
                            
                            # 정책
                            - 응답은 정확히 위의 JSON 형식으로 작성해주세요.
                            - 제공된 텍스트의 주요 내용을 간략히 요약하세요, 이모티콘이나 스티커는 무시하고 텍스트에만 집중해주세요.
                            - 불필요한 조언이나 평가는 하지 마세요.
                        """},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=500,
        )
        
        # JSON 응답을 파싱
        try:
            analysis_dict = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # JSON 파싱에 실패한 경우 기본값 설정
            analysis_dict = {
                "대화내용": "대화를 분석하지 못했습니다. 다시 이미지를 제공해주세요.",
                "성적표현": False,
                "부적절관계": False
            }

        results.append({
            "filename": file.filename,
            "analysis": analysis_dict
        })
    return {"results": results}