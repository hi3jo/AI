import openai
from PIL import Image as PILImage
import requests
from io import BytesIO
from fastapi import HTTPException
from src.core.webtoon.utils.make_text_box import make_korean_balloons
from src.core.webtoon.utils.set_webtoon_style import set_webtoon_style
from src.core.webtoon.utils.seperate_story import seperater_contents
from src.core.webtoon.utils.combine_images import combine_images_fix_size
from src.core.webtoon.utils.encode_image import b64encode
from src.core.webtoon.utils.hug_sum import sum
from src.core.webtoon.utils.make_prompt import generate_prompt
import time

# 사용자 요청을 기반으로 프롬프트 생성

def generate_webtoon(content):

    try:
        
        #context = ["타지로 이사와서 의지할 사람이 당신밖에 없었잖아.", "한번만 더 이런 일 있으면 이혼할 거라고 했잖아.", "회식이라고 나가더니 새벽 2시에 들어와서 정말 찝찝했어.", "헉, 폰을 뒤졌더니 폰번호 보낸 거랑 통화녹음이 있더라."]
       
        content = [  "남편이 요즘 나에게 소원해짐"
                   , "알고 봤더니 20대 동료와 바람피는 대화를 발견함. 성적인 대화를 발견함"
                   , "남편 잘못으로 내가 이혼을 요구함"
                   , "남편이 뻔뻔하게 거절하고 있음"]
        
        style_prompt = set_webtoon_style()
        
        images = []
        start_time = time.time()
        for i, text in enumerate(content):
            
            #prompt = generate_prompt(i, text) + f"/n Create a {style_prompt}"
            prompt = generate_prompt(i, text)
            response = openai.Image.create(
                model="dall-e-3"                        # 사용할 이미지 모델명
                , prompt=prompt
                , size="1024x1024"
                , n=1
            )
                
            image_url = response['data'][0]['url']
                
            # 이미지 다운로드 및 처리
            response = requests.get(image_url)
            img = PILImage.open(BytesIO(response.content))
            images.append(img)

            # 이미지에 한글 말풍선 추가
            #img = make_korean_balloons(img, summary)

        # 이미지를 2x2 그리드로 합치기
        combined_img = combine_images_fix_size(images)

        # 이미지를 base64로 인코딩
        buffered = BytesIO()
        combined_img.save(buffered, format="PNG")
        img_str = b64encode(combined_img)
        
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
    
           # 공통 캐릭터와 설정
        #character_description = "Same character appears in all frames, consistent appearance"
