import openai
from PIL import Image as PILImage
import requests
from io import BytesIO
import base64
from fastapi import HTTPException

def generate_webtoon(content):
    print("2.dalle3_ai.py : webtoon_api로 부터 전달받은 story : ", content)
    try:
        generated_images = []  # Dalle3로부터 생성된 이미지를 담을 리스트

        style_prompt = """
            웹툰 스타일:
            - 매우 상세하고 사실적인 한국 웹툰 스타일
            - 캐릭터들은 큰 눈, 작은 입, 뾰족한 턱을 가진 아름다운 외모
            - 남성 캐릭터는 짙은 눈썹, 날카로운 턱선, 세련된 헤어스타일
            - 여성 캐릭터는 긴 머리, 큰 눈, 부드러운 얼굴 선
            - 배경은 단순하지만 효과적으로 분위기를 전달
            - 흑백 톤에 가까운 색상 사용, 약간의 음영 처리
            - 대화 말풍선은 단순하고 깔끔한 디자인
            """
            
        # full_prompt = f"{style_prompt}\n\n스토리 내용: {story_content}\n\n이 스타일과 내용으로 4컷 웹툰을 생성해주세요."
    



        # 각 패널의 내용
        panels = [
            "타지역으로 이사와서 아무도 없는곳에 의지하며 같이 일하면서 살았어요. 이사온지 1년도 안되서 회사동생이랑 주점가서 걸렸네요. 멍청하게 본인이 녹음해서요. 싹싹 빌더니 용서했어요. 나는 투아웃이라고 한번만 더 이런일 있음 이혼이라고.",
            "2년동안 잠잠하다 했더니 회식이라고 나가더니 새벽 2시에 들어왔는데 굉장히 찝찝하고 미칠 것 같아서 폰을 뒤졌더니 자기 톡으로 폰번호 보낸 거 있어서 전화했더니 여자네요.",
            "폰뱅킹 이체내역도 있고 통화녹음도 있네요. 진짜 눈물이.. 대체 왜 이러는지.. 너무 열받아 잠도 못 자고 글 씁니다.",
            "왜 그럴까요.. 이혼이 답이겠죠? 다행히 아이 없습니다."
        ]

        # 프롬프트 스타일

        for i, panel in enumerate(panels):
            prompt = style_prompt + panel
            
            # OpenAI API로 전달할 데이터
            response = openai.Image.create(
                model="dall-e-3",  # 사용할 이미지 모델명
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                n=1
            )

            image_url = response['data'][0]['url']
            print(f"Generated image for panel {i+1}: {image_url}")
            generated_images.append(image_url)

        # 모든 이미지를 다운로드 및 합치기
        images = []
        for image_url in generated_images:
            response = requests.get(image_url)
            img = PILImage.open(BytesIO(response.content))
            images.append(img)

        # 4개의 이미지를 하나로 합침
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = PILImage.new('RGB', (total_width, max_height))

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.width

        # 이미지를 base64로 인코딩
        buffered = BytesIO()
        new_im.save(buffered, format="PNG")
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