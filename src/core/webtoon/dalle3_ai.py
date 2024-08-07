from dotenv import load_dotenv
import openai
import os
from PIL import Image as PILImage
import requests
from io import BytesIO
from fastapi import HTTPException
from src.core.webtoon.utils.make_text_box import make_korean_balloons
from src.core.webtoon.utils.set_webtoon_style import set_webtoon_style
from src.core.webtoon.utils.seperate_story import separate_contents
from src.core.webtoon.utils.combine_images import combine_images_fix_size
from src.core.webtoon.utils.encode_image import b64encode
from src.core.webtoon.utils.hug_sum import sum
from src.core.webtoon.utils.make_prompt import generate_prompt
from src.core.webtoon.utils.summarize_story import summarize_story
import time

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
openai.api_key = api_key

def generate_webtoon(content):

    try:

        # 개행 없애고 한 줄로 이어붙이기
        content_one_line = content.replace('\n', ' ').replace('    ', ' ').replace('  ', ' ')
        # 요약하기
        sum_text = summarize_story(content_one_line)
        
        # 요약 4단락으로 나누기
        targets = separate_contents(sum_text)
        
        # 웹툰 스타일 지정
        style_prompt = set_webtoon_style()
        
        images = []
        start_time = time.time()
        for i, text in enumerate(targets):
            no = i+1;
            # 사용자 요청
            #user_request = f"{text} \n {style_prompt}"
            prompt = generate_prompt(no, text, style_prompt)
            
            model = "dall-e-3"
            
            # 기존 버전에서의 호출 방식 : OpenAI API로 전달할 데이터
            """ response = openai.Image.create(
                  prompt=prompt
                , size="1024x1024"
                , n=1
            ) """
            
            # 변경 된 호출방식
            response = openai.images.generate(prompt=prompt, model=model)
                
            image_url = response.data[0].url  # data 속성에 직접 접근
                
            # 이미지 다운로드 및 처리
            response = requests.get(image_url)
            img = PILImage.open(BytesIO(response.content))
            
            # 한국어 넣기.
            img = make_korean_balloons(img, text)
            
            # 이미지를 리스트에 적재
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
#context = ["타지로 이사와서 의지할 사람이 당신밖에 없었잖아.", "한번만 더 이런 일 있으면 이혼할 거라고 했잖아.", "회식이라고 나가더니 새벽 2시에 들어와서 정말 찝찝했어.", "헉, 폰을 뒤졌더니 폰번호 보낸 거랑 통화녹음이 있더라."]
#prompt = generate_prompt(i, text) + f"/n Create a {style_prompt}"
#  content = [  "타지역으로 이사와서 아무도 없는 곳에서 의지하며 함께 일하면서 생활했습니다. 이사온 지 1년도 안 되어 회사 동료와 주점에 갔다가 발각되었습니다. 남편이 본인이 녹음한 내용을 들키는 실수를 저질렀고, 이후 싹싹 빌며 용서를 구했기에 저는 한 번만 더 이런 일이 있으면 이혼하겠다고 경고했습니다."
#                    , "처음 사건 이후 2년 동안 잠잠한 상태가 지속되었습니다. 저는 남편이 경고를 진지하게 받아들이고 있다고 생각했습니다. 하지만 어느 날, 남편이 회식이라고 나갔다가 새벽 2시에 돌아왔고, 그의 행동이 매우 찝찝하게 느껴졌습니다."
#                    , "남편의 행동이 수상하게 여겨져 그의 휴대폰을 뒤졌습니다. 그 결과, 자신의 톡으로 다른 여성의 전화번호를 보낸 것을 발견했습니다. 통화 녹음과 폰뱅킹 이체 내역도 확인되었습니다. 이러한 증거들을 접하며 저는 큰 충격을 받았습니다."
#                    , "너무나도 열받고 눈물이 나서 잠을 잘 수가 없었습니다. 남편이 왜 이런 행동을 반복하는지 이해할 수 없었습니다. 이혼이 답일까요? 다행히 아이는 없습니다. 저는 이 상황을 어떻게 해결해야 할지 깊이 고민하고 있습니다."]
