import openai
from PIL import Image as PILImage
import requests
from io import BytesIO
import base64
from fastapi import HTTPException
from core.webtoon.utils.make_text_box import make_korean_balloons

def seperater_contents(sentence):
    # 텍스트를 무조건 4단락으로 나누기
    num_prompts = 4
    sentence_length = len(sentence)
    chars_per_prompt = sentence_length // num_prompts
    prompts = []

    for i in range(num_prompts):
        start_idx = i * chars_per_prompt
        if i == num_prompts - 1:
            end_idx = sentence_length  # 마지막 단락은 끝까지
        else:
            end_idx = (i + 1) * chars_per_prompt
        prompt = sentence[start_idx:end_idx].strip()
        prompts.append(prompt)

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
        - 말풍선 없이
        - 영어 텍스트 들어가지 않게
    """
    return style_prompt

def generate_webtoon(content):
    try:
        
        cls = "one"
        
        context = [
            "타지로 이사와서 의지할 사람이 당신밖에 없었잖아.",
            "한번만 더 이런 일 있으면 이혼할 거라고 했잖아.",
            "회식이라고 나가더니 새벽 2시에 들어와서 정말 찝찝했어.",
            "헉, 폰을 뒤졌더니 폰번호 보낸 거랑 통화녹음이 있더라."]
        
        style_prompt = set_webtoon_style()
        sep_texts = seperater_contents(content)
        
        # 프롬프트 생성
        # 공통 캐릭터와 설정
        character_description = "Same character appears in all frames, consistent appearance"

        # 프롬프트 생성
        prompt_base = f"{content}, {character_description}"
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

            img = img.resize((512, 512))  # 512x512로 리사이즈

            # 이미지에 한글 말풍선 추가
            img = make_korean_balloons(img, context[i])
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