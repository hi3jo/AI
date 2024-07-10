import openai
from PIL import Image as PILImage
import requests
from io import BytesIO
import base64
from fastapi import HTTPException
import time

# prompt가 적용되지 않은, 사용자로부터 전달받은 사연으로 dalle3에게 4개의 칸으로 나뉜 1개의 이미지 생성 요청
# 생성되는 시간이 적게 소요 됨.
def generate_webtoon(content):
    
    print("1.basic_dalle3_ai.py : webtoon_api로 부터 전달받은 story : ", content)
    try:
        
        start_time = time.time()                                            # 시간 측정 시작

        # OpenAI API로 전달할 데이터
        response = openai.Image.create(
              model="dall-e-3"                                              # 사용할 이미지 모델명
            , prompt=content
            , size="1024x1024"
            , quality="hd"
            , n=1
        )

        image_url = response['data'][0]['url']
        #print("3.generated_image_url : ", image_url)

        # 이미지 다운로드 및 처리
        response = requests.get(image_url)
        img = PILImage.open(BytesIO(response.content))

        # 이미지를 base64로 인코딩
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        end_time = time.time()                                              # 시간 측정 종료
        print(f"Image generation time: {end_time - start_time} seconds")

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