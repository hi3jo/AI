import openai
from PIL import Image as PILImage
import requests
from io import BytesIO
import base64
from fastapi import HTTPException
from core.webtoon.utils.make_text_box import make_korean_balloons

def seperater_contents(sentence):
    # 문장을 일정 길이로 나누기
    max_chars_per_prompt = 50  # 한 번에 처리할 최대 글자 수
    prompts = []
    for i in range(0, len(sentence), max_chars_per_prompt):
        prompt = sentence[i:i + max_chars_per_prompt].strip()
        prompts.append(prompt)

    # 최소 4장, 최대 6장까지 사용
    prompts = prompts[:4]
    if len(prompts) < 4:
        while len(prompts) < 4:
            prompts.append(prompts[-1])  # 마지막 문장을 반복하여 최소 4장을 맞춤

    return prompts

def set_webtoon_style():
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
    return style_prompt

def generate_webtoon_copy(content):
    try:
        style_prompt = set_webtoon_style()
        sep_texts = seperater_contents(content)
        
        # 프롬프트 생성
        prompt_base = f"{content}, no text, no english"
        images = []
        for i, text in enumerate(sep_texts):
            prompt = f"{prompt_base} {text}" + style_prompt
            response = openai.Image.create(
                model="dall-e-3",  # 사용할 이미지 모델명
                prompt=prompt,
                size="1024x1024",
                n=1
            )
            
            image_url = response['data'][0]['url']
            
            # 이미지 다운로드 및 처리
            response = requests.get(image_url)
            img = PILImage.open(BytesIO(response.content))

            # 이미지에 한글 말풍선 추가
            img = make_korean_balloons(img)
            images.append(img)

        # 이미지를 2x2 그리드로 합치기
        grid_size = 1024
        combined_img = PILImage.new('RGB', (grid_size * 2, grid_size * 2))

        combined_img.paste(images[0], (0, 0))
        combined_img.paste(images[1], (grid_size, 0))
        combined_img.paste(images[2], (0, grid_size))
        combined_img.paste(images[3], (grid_size, grid_size))
        
        # 이미지를 base64로 인코딩
        buffered = BytesIO()
        combined_img.save(buffered, format="PNG")
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