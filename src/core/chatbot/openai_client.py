import openai
import os
import json
import logging
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate #질문 분류 프롬프트

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

# API 키가 제대로 로드되었는지 확인
if not openai.api_key:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

# 대화기록 저장을 위한 ChatMessageHistory 초기화
chat_history = ChatMessageHistory()

# 질문을 분류하는 함수
def classify_question(query_text):
    # ChatPromptTemplate를 사용하여 분류 프롬프트 생성
    prompt_template = ChatPromptTemplate.from_template('''
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
       Example: "계속된 폭행 등으로 혼인이 파탄됐어"
    3. 재산분할 - Division of joint property
       Example: "이혼 시 공동 재산을 어떻게 나눌 수 있나요?"
    4. 위자료 - Compensation for mental suffering
       Example: "숙려기간에 다른 이성과 교제한 남편에게 위자료 청구할 수 있어?"
    5. 생활비 - Non-payment of living expenses
       Example: "생활비를 주지 않는데 이혼할 수 있을까요?"
    6. 성기능 장애 - Marital annulment due to sexual dysfunction
       Example: "성기능 장애로 혼인취소 할 수 있어?"
    7. 혼외자 출산 - Family breakdown due to extramarital childbirth
       Example: "남편이 다른 여성과 혼외자를 출산했어"
    8. 유책배우자 - Divorce claims from at-fault spouse
       Example: "유책배우자가 이혼청구 할 수 있나요?"
    9. ETC question - Questions not covered by the above categories.
       Example: "이혼 후 양육권은 어떻게 결정되나요?"
    ''')

    # 분류 요청 메시지 생성
    classification_messages = [
        {"role": "system", "content": "You are a professional and accurate text classifier machine and translator machine."},
        {"role": "user", "content": prompt_template.format(query_text=query_text)}
    ]

    try:
        # OpenAI의 ChatCompletion API를 사용하여 질문 분류 요청
        classification_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=classification_messages,
            max_tokens=500
        )
        logger.info(f"OpenAI 질문 분류 응답 생성 완료: {classification_response}")
        
        # 응답 내용 추출 및 로그에 기록
        classified_question_content = classification_response['choices'][0]['message']['content']
        logger.info(f"응답 내용: {classified_question_content}")

        # 불필요한 문자를 제거하고 JSON 형식으로 변환
        classified_question_content = classified_question_content.replace('```json', '').replace('```', '').strip()
        classified_question = json.loads(classified_question_content)
        return classified_question
    except json.JSONDecodeError as e:
        logger.error(f"JSON 디코딩 오류: {e}")
        raise ValueError("질문 분류 중 JSON 디코딩 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"OpenAI 질문 분류 응답 생성 중 오류 발생: {e}")
        raise ValueError("질문 분류 중 오류가 발생했습니다.")

# 응답을 생성하는 함수
def generate_response(query_text, question_type, chat_history, first_interaction=False, similar_docs=None, most_similar_info=None, max_context_length=16385):
    # 응답 프롬프트 정의
    response_prompt = f'''
    # Role
    You are a helpful assistant.

    # Task
    Provide a detailed and informative answer to the following question based on its type. Please provide the response in Korean.

    ## Question
    "{query_text}"

    ## Classified Question Type
    "{question_type}"

    # Response
    '''

    # 이전 대화기록을 포함한 메시지 생성 (최대 컨텍스트 길이를 초과하지 않도록 제한)
    context_messages = chat_history.messages[-max_context_length:] if len(chat_history.messages) > max_context_length else chat_history.messages
    response_messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ] + context_messages + [
        {"role": "user", "content": response_prompt}
    ]

    try:
        # OpenAI의 ChatCompletion API를 사용하여 응답 생성 요청
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=response_messages,
            max_tokens=500
        )
        logger.info(f"OpenAI 응답 생성 완료: {response}")
        final_response = response['choices'][0]['message']['content']
        
        # 첫 번째 인터랙션일 경우 추가 정보 저장
        if first_interaction and similar_docs and most_similar_info:
            chat_history.add_message({"role": "system", "content": f"Results: {similar_docs}"})
            chat_history.add_message({"role": "system", "content": f"Most similar info: {most_similar_info}"})
        
        return final_response
    except Exception as e:
        logger.error(f"OpenAI 응답 생성 중 오류 발생: {e}")
        raise ValueError("OpenAI 응답 생성 중 오류가 발생했습니다.")
