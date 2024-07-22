import openai
import pandas as pd
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

def process_kdrama_data(csv_path):
    # CSV 파일을 읽어옵니다.
    df = pd.read_csv(csv_path)

    # 데이터프레임의 내용을 확인합니다.
    print("데이터프레임 내용:")
    print(df.head())

    # '판례내용' 컬럼의 텍스트를 하나의 문자열로 결합합니다.
    full_text = " ".join(df['판례내용'].astype(str).tolist())

    # OpenAI 임베딩을 사용하여 의미론적 청크 분할기를 초기화합니다.
    text_splitter = SemanticChunker(OpenAIEmbeddings())

    # 텍스트를 의미론적으로 관련된 청크로 분할합니다.
    chunks = text_splitter.split_text(full_text)

    # 분할된 청크를 출력합니다.
    print("\n분할된 청크:")
    for i, chunk in enumerate(chunks):
        print(f"[Chunk {i}]\n")
        print(chunk)
        print("=" * 60)

    # 분할된 청크를 문서로 변환합니다.
    docs = text_splitter.create_documents([full_text])

    # 문서의 내용을 출력합니다.
    print("\n문서 내용:")
    for i, doc in enumerate(docs):
        print(f"[Document {i}]\n")
        print(doc.page_content)
        print("=" * 60)

    # 분할된 문서의 개수를 출력합니다.
    print(f"총 문서 개수: {len(docs)}")
    
    return docs

def ask_openai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 사용할 모델 지정
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ],
            max_tokens=150,  # 답변의 최대 토큰 수
            n=1,
            stop=None,
            temperature=0.7
        )
        answer = response['choices'][0]['message']['content']
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    csv_path = './divorce.csv'
    docs = process_kdrama_data(csv_path)
    
    print("\nOpenAI에 질문하세요 (종료하려면 'exit' 입력):")
    while True:
        user_input = input("질문: ")
        if user_input.lower() == 'exit':
            break
        answer = ask_openai(user_input)
        print("답변:", answer)

if __name__ == "__main__":
    main()
