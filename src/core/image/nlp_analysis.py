import openai
import os
import json
import logging
from dotenv import load_dotenv
# from src.core.image.pro_ocr import preprocess_text, preprocess_image_with_color_mask, remove_hand_region, extract_text_regions, extract_relevant_text, is_relevant_text, is_excluded_text

logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

# API 키가 제대로 로드되었는지 확인
if not openai.api_key:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

def classify_text(analyze_text):
    classification_prompt = f'''
    # Role
    You are a professional and accurate text classifier machine and translator machine.

    # Output Format
    {{
    "analyze": "{analyze_text}",
    "analyze_type": "{{{{analyze_type}}}}",
    "summary": "{{{{summary}}}}"
    }}

    # Task
    - The ultimate goal is to classify the type of the analyze by referring the analyze.
    - To do that, Let's think step by step.
    - For information about analyze types, see "##Analyze Types".
    - This is very important to my career. Please do your best.
    - Additionally, provide a summary of the text, explaining the context of the conversation and the relationship between the people involved in Korean.
    - Point out any jokes or suggestive parts in the conversation.
    - Explicitly mention any sexual content or implications found in the text.

    ## Step 1
    - You will be provided with a '{analyze_text}' analyze delimited by triple quotes.

    ## Step 2 
    - Store the text image content in the variable "analyze".

    ## Step 3
    - Classify the analyze type by referring the "analyze" extracted from the "Step 2" for the '{analyze_text}'.

    ## Step 4
    - Summarize the text in Korean and provide additional analysis as requested in the Task section.

    # Policy
    - Do not write any content other than the json string, because the resulting json string must be used directly in the script.
    - Do not write unnecessary explanations or instructions.
    - You must select one of the analyze types above.
    - You must respond with the content specified in the prompt.
    - If there is insufficient information to classify, select "ETC analyze"

    # Context
    ## sexual expression
    1. 벌려 - Open it, Spread it, Separate it
    Example: "나 없을 때 다른 사람한테 벌려주지 말고." - "Don't spread your legs for someone else when I'm not around"
    이 문장에서 "벌려"는 명백한 성적 의미를 가집니다. 다리를 벌리는 행위를 암시하며, 성적인 행위와 연관됩니다.
    2. 모텔 - Motel
    Example: "모텔갈까?"
    3. 야한 - sexual
    Example: "야한 사진 있으면 보내줘"
    4. 홍콩 - Hongkong
    Example: "내가 홍콩 보내줄게."

    ## Slang Explanation
    - 다음은 한국어 슬랭 표현들에 대한 설명입니다:
      1. 'ㅋㅋ': 웃음을 나타내는 표현으로, 영어의 'LOL'과 유사합니다.
      2. 'ㅎㅎ': 웃음을 나타내는 표현으로, 'ㅋㅋ'보다 부드럽게 웃는 느낌입니다.
      3. 'ㅇㅇ': '응응'의 축약형으로, 긍정의 뜻을 나타냅니다.
      4. 'ㅜㅜ': 우는 얼굴을 나타내며, 슬픔이나 실망을 표현합니다.
      5. 'ㅠㅠ': 'ㅜㅜ'와 같은 의미로, 우는 얼굴을 나타내며 슬픔이나 실망을 표현합니다.
    - 위 설명을 바탕으로, 한국어 슬랭 표현들을 이해하고 분석에 반영해 주세요.

    ## Analysis Request
    - Please analyze the following text:
    "{analyze_text}"
    "Describe the overall mood and context of this conversation and infer the relationship between the two people."
    "Finally, make sure to include whether there are any sexual expression set in #Context, and provide a comprehensive evaluation in Korean."
    "Very important, please make sure you have any sexual content in the conversation and respond."
    "If a word set under '## sexual expression' is identified, it will unconditionally be considered a sexual expression."
    '''

    classification_messages = [
        {"role": "system", "content": "You are a professional and accurate text classifier machine and translator machine."},
        {"role": "user", "content": classification_prompt}
    ]

    try:
        classification_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=classification_messages,
            max_tokens=800
        )
        logger.info(f"OpenAI 분석 분류 응답 생성 완료: {classification_response}")
        
        # 응답 내용을 문자열로 먼저 출력하여 확인
        classified_analyze_content = classification_response['choices'][0]['message']['content']
        logger.info(f"응답 내용: {classified_analyze_content}")

        # 불필요한 문자 제거 (```json 및 ```)
        classified_analyze_content = classified_analyze_content.replace('```json', '').replace('```', '').strip()

        # JSON 형식이 맞는지 검증
        classified_analyze = json.loads(classified_analyze_content)

        return classified_analyze
    except json.JSONDecodeError as e:
        logger.error(f"JSON 디코딩 오류: {e}")
        raise ValueError("분석 분류 중 JSON 디코딩 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"OpenAI 분석 분류 응답 생성 중 오류 발생: {e}")
        raise ValueError("분석 분류 중 오류가 발생했습니다.")

def analyze_text_from_image(image_path):
    """
    이미지에서 텍스트를 추출하고 분석하는 함수.
    """
    text = extract_relevant_text(image_path)  # 전처리 및 텍스트 추출

    if text:
        return classify_text(text)
    else:
        return {"error": "No relevant text found in the image"}
