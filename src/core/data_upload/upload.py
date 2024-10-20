# 1 upload.py
# 임베딩 모델 로드 및 문서 처리
# CSV 파일 로드
# 텍스트 청크 및 임베딩 생성

import pandas as pd
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import chromadb
import logging
import os

# 공통 설정 임포트
from src.core.data_upload.config import logger

# 임베딩 모델 로드 (SentenceTransformer 사용)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# ChromaDB 클라이언트 초기화
client = chromadb.PersistentClient(path="./data")

# 컬렉션 가져오기 또는 생성
def get_or_create_collection(client, collection_name):
    try:
        collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
        logger.info(f"컬렉션 '{collection_name}' 가져오기 또는 생성 성공")
    except Exception as e:
        logger.error(f"컬렉션 가져오기 또는 생성 실패: {e}")
        collection = None
    
    # 현재 존재하는 모든 컬렉션 출력
    try:
        existing_collections = client.list_collections()
        logger.info(f"현재 존재하는 컬렉션들: {[col.name for col in existing_collections]}")
    except Exception as e:
        logger.error(f"현재 존재하는 컬렉션 조회 실패: {e}")
    
    return collection

# 컬렉션 생성 또는 가져오기
collection = get_or_create_collection(client, "case-law3")

# 텍스트 길이 계산 함수
def tiktoken_len(text):
    return len(text)

# CSV 파일 로드 및 텍스트 청크 생성 함수 정의
def load_csv(file_path):
    try:
        # 잘못된 행 건너뛰기
        df = pd.read_csv(file_path, on_bad_lines='skip')
        docs = []
        for _, row in df.iterrows():
            # 판례내용과 메타데이터 저장
            text = row['판례내용']
            metadata = {
                "판례일련번호": row["판례일련번호"],
                "사건명": row.get("사건명", "없음"),
                "사건번호": row.get("사건번호", "없음"),
                "법원명": row.get("법원명", "없음"),
                "판결요지": row.get("판결요지", "없음") 
            }
            docs.append(Document(page_content=text, metadata=metadata))
        logger.info("CSV 파일 로드 성공")
        return docs
    except Exception as e:
        logger.error(f"CSV 파일 로드 실패: {e}")
        return None

# 텍스트 청크 생성 함수 정의
def get_text_chunks(documents):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=tiktoken_len
        )
        chunks = text_splitter.split_documents(documents)
        logger.info("텍스트 청크 처리 성공")
        return chunks
    except Exception as e:
        logger.error(f"텍스트 청크 처리 실패: {e}")
        return None

# 텍스트 임베딩 생성 및 벡터 데이터베이스에 저장 함수 정의
def embed_and_store_documents(docs):
    chunked_docs = get_text_chunks(docs)
    if chunked_docs is None:
        return {"message": "텍스트 청크 처리 실패"}

    texts = [doc.page_content for doc in chunked_docs]
    metadatas = [doc.metadata for doc in chunked_docs]

    # 텍스트 임베딩 생성
    logger.info("임베딩 모델 함수 호출 시작...")
    try:
        embeddings = model.encode(texts, convert_to_tensor=False)
        if embeddings is None or len(embeddings) == 0:
            raise ValueError("임베딩 생성 실패")
        logger.info(f"임베딩 모델 함수 호출 완료, 생성된 임베딩 수: {len(embeddings)}")
    except Exception as e:
        logger.error(f"임베딩 모델 함수 호출 실패: {e}")
        return {"message": "임베딩 생성 실패"}

    # Chroma 벡터 데이터베이스에 문서 추가
    try:
        logger.info("벡터 DB 저장중입니다...")
        ids = [f"case-{i}" for i in range(len(texts))]
        collection.add(
            embeddings=embeddings,
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        logger.info("벡터 데이터베이스에 저장 성공")
    except Exception as e:
        logger.error(f"벡터 데이터베이스에 저장 실패: {e}")
        return {"message": "벡터 데이터베이스에 저장 실패"}

    return {"message": "ChromaDB에 저장되었습니다.", "num_documents": len(chunked_docs)}
