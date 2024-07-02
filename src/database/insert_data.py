import pandas as pd
import chromadb
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# 3.1.벡터 DB 로드 함수
def load_vector_db():
    try:
        chroma_client = chromadb.PersistentClient(path="./chroma.sqlite3")
        collection = chroma_client.get_or_create_collection(name="divorce_precedent")
        print("벡터 데이터베이스 로드 성공")
        return collection
    except Exception as e:
        print(f"벡터 데이터베이스 로드 실패: {e}")
        return None

# 1. CSV 데이터 로드 함수
def load_csv_data():
    try:
        df = pd.read_csv('crawling2024.csv')
        documents = [Document(page_content=row['판례내용'], metadata={"id": str(row['판례일련번호'])}) for _, row in df.iterrows()]
        print("CSV 데이터 로드 성공")
        return documents
    except Exception as e:
        print(f"CSV 데이터 로드 실패: {e}")
        return None

# 텍스트 길이 계산 함수
def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)

# 2. 텍스트 청크 처리 함수
def get_text_chunks(documents):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=900,
            chunk_overlap=100,
            length_function=tiktoken_len
        )
        chunks = text_splitter.split_documents(documents)
        print("텍스트 청크 처리 성공")
        return chunks
    except Exception as e:
        print(f"텍스트 청크 처리 실패: {e}")
        return None

# 임베딩 모델 생성 함수
def get_embeddings():
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("임베딩 모델 생성 성공")
        return embeddings
    except Exception as e:
        print(f"임베딩 모델 생성 실패: {e}")
        return None

# 벡터 스토어 생성 및 데이터 저장 함수
def save_to_vectorstore(text_chunks):
    embeddings = get_embeddings()
    if embeddings is None:
        print("임베딩 모델을 로드할 수 없습니다.")
        return None

    collection = load_vector_db()
    if collection is None:
        print("벡터 데이터베이스를 로드할 수 없습니다.")
        return None

    try:
        for i, chunk in enumerate(text_chunks):
            chunk_id = f"doc_{i}_{chunk.metadata['id']}"
            embedding = embeddings.embed_documents([chunk.page_content])[0]

            print("1.[chunk.page_content, 텍스트 데이터] : ", [chunk.page_content])
            collection.add(
                ids=[chunk_id],
                documents=[chunk.page_content],
                metadatas=[{"chunk_id": chunk_id}],
                embeddings=[embedding]
            )
        print("벡터 스토어 저장 성공")
        return collection
    except Exception as e:
        print(f"벡터 스토어 저장 실패: {e}")
        return None

# 메인 함수
def main():
    
    # 1. 저장할 데이터를 가지고 있는 csv파일을 적재한다.
    documents = load_csv_data()
    if documents is None:
        print("CSV 데이터를 로드할 수 없습니다.")
        return

    # 2. 데이터를 작업하기 쉽게 분할하고 묶는다.  
    text_chunks = get_text_chunks(documents)
    if text_chunks is None:
        print("텍스트 청크를 처리할 수 없습니다.")
        return

    # 3. 벡터 DB로 데이터를 insert 한다.
    vectorstore = save_to_vectorstore(text_chunks)
    if vectorstore is None:
        print("벡터 스토어를 생성할 수 없습니다.")
        return

    print('VectorDB로 csv내 데이터 저장 완료!')

if __name__ == '__main__':
    main()