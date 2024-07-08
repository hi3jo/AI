import openai
from PIL import Image as PILImage
import requests
from io import BytesIO
import base64
from fastapi import HTTPException
from src.core.webtoon.make_balloons import make_korean_balloons

def generate_webtoon(content):
    
    #print("2.dalle3_ai.py : webtoon_api로 부터 전달받은 story : ", content)
    try:
        
        style_prompt = """
            웹툰 스타일:
            - 매우 상세하고 사실적인 한국 웹툰 스타일
            - 캐릭터들은 일반적인 한국 사람들의 얼굴
            - 남성 캐릭터는 찌질하고 스포츠컷 머리
            - 여성 캐릭터는 긴 머리, 큰 눈, 부드러운 얼굴 선
            - 배경은 단순하지만 효과적으로 분위기를 전달
            - 다양한 컬러 사용, 약간의 음영 처리
            - 대화 말풍선은 단순하고 깔끔한 디자인
            """
        
        # 프롬프트 생성
        prompt = f"{content}, 4컷에서 6컷 사이의 웹툰 생성. 말풍선, 영어 텍스트 없이"
        # OpenAI API로 전달할 데이터
        response = openai.Image.create(
              model="dall-e-3"                                                                                  # 사용할 이미지 모델명
            , prompt=prompt + style_prompt
            , size="1024x1024"
            , quality="hd"
            , n=1
        )

        image_url = response['data'][0]['url']
        #print("3.generated_image_url : ", image_url)

        print("1...")
        # 이미지 다운로드 및 처리
        response = requests.get(image_url)
        
        print("2...")
        img = PILImage.open(BytesIO(response.content))

        print("3...")
        # 이미지에 한글 말풍선 추가
        img = make_korean_balloons(img)
        print("5...")
        # 이미지를 base64로 인코딩
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return img_str

    except openai.error.InvalidRequestError as e:
        print(f"InvalidRequestError: {e}")
        raise HTTPException(status_code=500, detail=f"Invalid request: {e}")
    except KeyError:
        print("API 응답에서 이미지 URL을 찾을 수 없습니다.")
        raise HTTPException(status_code=500, detail="Failed to parse image URLs from API response")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")