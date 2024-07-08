import openai
from PIL import Image as PILImage
import requests
from io import BytesIO
import base64
from fastapi import HTTPException

def generate_webtoon(content):
    
    print("2.dalle3_ai.py : webtoon_api로 부터 전달받은 story : ", content)
    try:
        
        generated_images = []                                                                                   # Dalle3로부터 생성 된 이미지를 담을 리스트
        
        prompt = f"{content} 앞에 내용을 가지고, 한국 웹툰 중 내 남편과 결혼해줘라 스타일로 4컷 웹툰을 그려줘. "
        # OpenAI API로 전달할 데이터
        response = openai.Image.create(
              model="dall-e-3"                                                                                  # 사용할 이미지 모델명
            , prompt=prompt
            , size="1024x1024"
            , quality="standard"
            , n=1,
        )

        image_url = response['data'][0]['url']
        print("3.generated_image_url : ", image_url)

        # 이미지 다운로드 및 처리
        response = requests.get(image_url)
        img = PILImage.open(BytesIO(response.content))

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