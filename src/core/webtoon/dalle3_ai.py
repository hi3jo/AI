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

# 사용자 요청을 기반으로 프롬프트 생성
def generate_prompt(user_input):
    # ChatGPT를 사용하여 프롬프트 생성
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that creates detailed prompts for generating images."},
            {"role": "user", "content": user_input}
        ]
    )
    prompt = response['choices'][0]['message']['content']
    return prompt

def generate_webtoon(content):

    try:
        
        #context = ["타지로 이사와서 의지할 사람이 당신밖에 없었잖아.", "한번만 더 이런 일 있으면 이혼할 거라고 했잖아.", "회식이라고 나가더니 새벽 2시에 들어와서 정말 찝찝했어.", "헉, 폰을 뒤졌더니 폰번호 보낸 거랑 통화녹음이 있더라."]
        # summary = sum(content)
        style_prompt = set_webtoon_style()
        prompt = generate_prompt(content)
        
        print("prompt를 보자 : ", prompt)
        response = openai.Image.create(
              model="dall-e-3"  # 사용할 이미지 모델명
            , prompt=prompt
            , size="1024x1024"
            , n=1
        )
            
        image_url = response['data'][0]['url']
            
        # 이미지 다운로드 및 처리
        response = requests.get(image_url)
        img = PILImage.open(BytesIO(response.content))

        # 이미지에 한글 말풍선 추가
        #img = make_korean_balloons(img, summary)

        # 이미지를 base64로 인코딩
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = b64encode(img)
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
    
    
            # prompt_base = """
        
        #     첫 번째 패널:

        #         배경: 새로운 도시에서의 삶 시작
                   # 공원치에 남자 여자가 손잡고 ㅇ앉아있는 그림.
        #         scene: "타지역으로 이사와서 아무도 없는곳에 의지하며 같이 일하면서 살았어요."


        #     두 번째 패널
        #         배경: 회사 동생과의 사건
        #         scene: "이사온지 1년도 안되서 회사동생이랑 주점가서 걸렸네요. 멍청하게 본인이 녹음해서요. 싹싹 빌더니 용서했어요."


        #     세번째 패널
        #         배경: 남편의 두 번째 배신
        #         scene: "회식이라고 나가더니 새벽 2시에 들어왔는데 굉장히 찝찝하고 미칠것같아서 폰을 뒤졌더니 자기톡으로 폰번호 보낸거 있어서 전회했더니 여자네요."
        #         네 번째 패널:

        #     네번째 패널 
            
        #         배경: 결심과 결론
        #         scene: "폰뱅킹 이체내역도 있고 통화녹음도 있네요. 진짜 눈물이..대체 왜 이러는지.. 이혼이 답이겠죠? 다행히 아이 없습니다."
        
        # 이 4개의 패널을 가지고 4컷 웹툰 생성해줘
        # """
    
    
           # 공통 캐릭터와 설정
        #character_description = "Same character appears in all frames, consistent appearance"
