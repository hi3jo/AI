import os
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.core.chatbot.chromadb_client import chroma_retriever, get_chroma_client
from src.core.chatbot.embeddings import ko_embedding  # 임베딩 모델을 임포트합니다

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일의 환경 변수를 로드
load_dotenv()

# OpenAI API 키 설정
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

# API 키가 제대로 로드되었는지 확인
if not client.api_key:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
else:
    logger.info("OpenAI API 키가 설정되었습니다.")

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
    1. 무정자증- Questions related to non-payment of child support
       Example: "남편이 무정자증에다 성염색체에 선천적 이상인데 혼인 취소 할수 있어?"
    2. 폭행 - Assault cases
       Example: "반복적으로 폭력을 행사하는데 이혼 청구 할 수 있어?"
    3. 재산분할 - Division of joint property
       Example: "공무원연금이 이혼 시 재산분할의 대상이 될 수 있어?"
    4. 위자료 - Compensation for mental suffering
       Example: "이혼 숙려기간에 다른 이성과 교제한 남편에게 위자료 청구할 수 있어?"
    5. 출산 경력 - Childbirth experience
       Example: "출산의 경력을 고지하지 않은게 혼인취소 사유 될 수 있어?"
    6. 성기능 장애 - Marital annulment due to sexual dysfunction
       Example: "성기능 장애로 혼인취소 할 수 있어?"
    7. 혼외자 출산 - Family breakdown due to extramarital childbirth
       Example: "남편이 다른 여성과 혼외자를 출산했어"
    8. 유책배우자 - Divorce claims from at-fault spouse
       Example: "유책배우자가 이혼 청구 할 수 있나요?"
    9. ETC question - Questions not covered by the above categories.
       Example: "재혼은 어떻게 해?"
    ''')

    # 분류 요청 메시지 생성
    classification_messages = [
        {"role": "system", "content": "You are a professional and accurate text classifier machine and translator machine."},
        {"role": "user", "content": prompt_template.format(query_text=query_text)}
    ]

    try:
        # OpenAI의 ChatCompletion API를 사용하여 질문 분류 요청
        classification_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=classification_messages,
            max_tokens=500
        )
        logger.info(f"OpenAI 질문 분류 응답 생성 완료: {classification_response}")
        
        # 응답 내용 추출 및 로그에 기록
        classified_question_content = classification_response.choices[0].message.content
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

# 질문에 대해 답변을 생성하는 함수
# 유사 문서를 찾은 후, 이를 기반으로 OpenAI를 통해 답변을 생성하는 코드
def get_answer(question):
    collection = get_chroma_client()
    docs, metadatas = chroma_retriever(query=question, collection=collection, embeddings=ko_embedding)
    if not docs:
        return {"message": "검색된 문서가 없습니다."}
    
    context = "\n\n".join([f"Document {idx+1}: {doc}" for idx, doc in enumerate(docs)])
    
    # OpenAI 모델의 최대 컨텍스트 길이를 초과하지 않도록 자릅니다.
    max_context_length = 4097 - 256  # 최대 토큰 길이에서 여유를 둡니다.
    if len(context) > max_context_length:
        context = context[:max_context_length]

    # OpenAI API를 사용하여 답변 생성
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable assistant who provides accurate answers based on the provided context."},
                {"role": "user", "content": f"Here are some legal documents:\n{context}\nBased on these documents, answer the following question: {question}"}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        final_response = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI 응답 생성 중 오류 발생: {e}")
        return {"message": "응답 생성 중 오류가 발생했습니다."}

    return final_response

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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=response_messages,
            max_tokens=500
        )
        logger.info(f"OpenAI 응답 생성 완료: {response}")
        final_response = response.choices[0].message.content.strip()

        # 성공 로그 추가
        logger.info(f"Response generated successfully: {final_response}")
        
        # 첫 번째 인터랙션일 경우 추가 정보 저장
        if first_interaction and similar_docs and most_similar_info:
            chat_history.add_message({"role": "system", "content": f"Results: {similar_docs}"})
            chat_history.add_message({"role": "system", "content": f"Most similar info: {most_similar_info}"})
        
        return final_response
    except Exception as e:
        logger.error(f"OpenAI 응답 생성 중 오류 발생: {e}")
        raise ValueError("OpenAI 응답 생성 중 오류가 발생했습니다.")
        
# Example usage of RunnableWithMessageHistory
class MyRunnableWithHistory(RunnableWithMessageHistory):
    def __init__(self, chat_history):
        self.chat_history = chat_history

    def run(self, query_text):
        classified_question = classify_question(query_text)
        response = generate_response(query_text, classified_question["question_type"], self.chat_history)
        return response
