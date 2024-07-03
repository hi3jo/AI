import openai
from PIL import Image as PILImage
import requests
from io import BytesIO
import base64
from fastapi import HTTPException

def generate_and_display_comic(long_sentence):
    
    print("1.long_sentence : ", long_sentence)
    try:
        # 문장을 일정 길이로 나누기
        max_chars_per_prompt = 100  # 한 번에 처리할 최대 글자 수
        prompts = []
        for i in range(0, len(long_sentence), max_chars_per_prompt):
            prompt = long_sentence[i:i + max_chars_per_prompt].strip()
            prompts.append(prompt)

        # 최소 4장, 최대 6장까지 사용
        prompts = prompts[:6]
        if len(prompts) < 4:
            while len(prompts) < 4:
                prompts.append(prompts[-1])  # 마지막 문장을 반복하여 최소 4장을 맞춤

        generated_images = []
        print("2.prompts : ", prompts)
        for i, prompt in enumerate(prompts):
            # 안전한 프롬프트 생성
            safe_prompt = f"Illustrate a webtoon scene: {prompt}. Make it safe and appropriate."
            response = openai.Image.create(
                model="dall-e-3",  # 사용할 이미지 모델명
                prompt=safe_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response['data'][0]['url']  # 이미지 URL 가져오기
            generated_images.append(image_url)
        print("3.generated_images : ", generated_images)
        # 하나의 이미지에 4분할하여 표시
        if len(generated_images) > 0:
            rows = 2
            cols = 2 if len(generated_images) >= 4 else 1
            combined_image = PILImage.new("RGB", (1024 * cols, 1024 * rows))  # 총 이미지 크기 설정

            for idx, image_url in enumerate(generated_images):
                response = requests.get(image_url)
                img = PILImage.open(BytesIO(response.content))
                img = img.resize((1024, 1024))  # 각 이미지 크기 조정

                # 이미지를 4분할하여 각 영역에 표시
                x = (idx % cols) * 1024
                y = (idx // cols) * 1024
                combined_image.paste(img, (x, y))

            # 결합된 이미지 base64 인코딩
            buffered = BytesIO()
            combined_image.save(buffered, format="PNG")
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