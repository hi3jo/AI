import openai
import os
import json
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

# API 키가 제대로 로드되었는지 확인
if not openai.api_key:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

def classify_question(query_text):
    classification_prompt = f'''
    # Role
    You are a professional and accurate text classifier machine and translator machine.

    # Output Format
    {{
    "question": "{query_text}",
    "question_type": "{{{{question_type}}}}"
    }}

    # Task
    - The ultimate goal is to classify the type of the question by referring the question.
    - To do that, Let's think step by step.
    - For information about question types, see "##Question Types".
    - This is very important to my career. Please do your best.

    ## Step 1
    - You will be provided with a '{query_text}' question delimited by triple quotes.

    ## Step 2
    - Store the question content in the variable "question".

    ## Step 3
    - Classify the question type by referring the "question" extracted from the "Step 2" for the '{query_text}'.

    # Policy
    - Do not write any content other than the json string, because the resulting json string must be used directly in the script.
    - Do not write unnecessary explanations or instructions.
    - You must select one of the question types above.
    - If there is insufficient information to classify, select "ETC question"

    # Context
    ## Question Types and Examples
    1. 양육비 - Questions related to non-payment of child support
       Example: "양육비를 지급하지 않는 남편에게 어떻게 대처해야 하나요?"
    2. 폭행 - Assault cases
       Example: "계속된 폭행 등으로 혼인이 파탄됐는데 이혼할 수 있나요?"
    3. 재산분할 - Division of joint property
       Example: "이혼 시 공동 재산을 어떻게 나눌 수 있나요?"
    4. 위자료 - Compensation for mental suffering
       Example: "숙려기간에 다른 이성과 교제한 남편에게 위자료 청구할 수 있어?"
    5. 생활비 - Non-payment of living expenses
       Example: "생활비를 주지 않는데 이혼할 수 있을까요?"
    6. 성기능 장애 - Marital annulment due to sexual dysfunction
       Example: "성기능 장애로 혼인취소 할 수 있어?"
    7. 혼외자 출산 - Family breakdown due to extramarital childbirth
       Example: "남편이 다른 여성과 혼외자를 출산했는데 이혼할 수 있어?"
    8. 유책배우자 - Divorce claims from at-fault spouse
       Example: "유책배우자가 이혼 청구 할 수 있나요?"
    9. ETC question - Questions not covered by the above categories.
       Example: "이혼 후 양육권은 어떻게 결정되나요?"
    '''

    classification_messages = [
        {"role": "system", "content": "You are a professional and accurate text classifier machine and translator machine."},
        {"role": "user", "content": classification_prompt}
    ]

    try:
        classification_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=classification_messages,
            max_tokens=500
        )
        logger.info(f"OpenAI 질문 분류 응답 생성 완료: {classification_response}")
        
        # 응답 내용을 문자열로 먼저 출력하여 확인
        classified_question_content = classification_response['choices'][0]['message']['content']
        logger.info(f"응답 내용: {classified_question_content}")

        # 불필요한 문자 제거 (```json 및 ```)
        # JSON 디코딩 오류를 해결한 핵심 부분
        # 문자열에서 ```json 및 ``` 문자를 제거하여 순수 JSON 형식으로 변환한 후 디코딩을 시도
        classified_question_content = classified_question_content.replace('```json', '').replace('```', '').strip()

        # JSON 형식이 맞는지 검증
        classified_question = json.loads(classified_question_content)
        return classified_question
    except json.JSONDecodeError as e:
        logger.error(f"JSON 디코딩 오류: {e}")
        raise ValueError("질문 분류 중 JSON 디코딩 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"OpenAI 질문 분류 응답 생성 중 오류 발생: {e}")
        raise ValueError("질문 분류 중 오류가 발생했습니다.")

def generate_response(query_text, question_type):
    response_prompt = f'''
    # Role
    You are a helpful assistant.

    # Task
    Provide a detailed and informative answer to the following question based on its type:

    ## Question
    "{query_text}"

    ## Classified Question Type
    "{question_type}"

    # Response
    '''

    response_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": response_prompt}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=response_messages,
            max_tokens=500
        )
        logger.info(f"OpenAI 응답 생성 완료: {response}")
        final_response = response['choices'][0]['message']['content']
        return final_response
    except Exception as e:
        logger.error(f"OpenAI 응답 생성 중 오류 발생: {e}")
        raise ValueError("OpenAI 응답 생성 중 오류가 발생했습니다.")
