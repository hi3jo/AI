import openai
import os
import logging
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

def generate_images():
    prompts = [
        "A person standing at a crossroads between divorce and reconciliation, in the detailed and emotional style of Japanese manga, with soft colors and expressive characters. The scene should depict a lush, nature-filled background with a sense of contemplation.",
        "Divorce reasons: The husband's infidelity and marital conflicts leading to the decision to divorce, illustrated in the dramatic and expressive style of Japanese manga, with detailed backgrounds and emotional characters showing deep distress.",
        "Part to resolve: Seeking solutions for rebuilding trust between the couple and addressing the husband's behavior, depicted in the hopeful and introspective style of Japanese manga, with characters looking determined and a soft, whimsical background.",
        "The moment of choosing between divorce and reconciliation, illustrated in the contemplative and detailed style of Japanese manga, with a soft color palette and characters showing a mix of emotions as they make their decision."
    ]

    image_urls = []
    for prompt in prompts:
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']
            image_urls.append(image_url)
        except Exception as e:
            logger.error(f"이미지 생성 중 오류 발생: {e}")
            raise ValueError("이미지 생성 중 오류가 발생했습니다.")
    return image_urls