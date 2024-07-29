from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
import logging
from .chroma_db import delete_collection, create_collection
from .data_processing import get_text_chunks
from dotenv import load_dotenv
import os

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

# HuggingFace 모델 이름 설정
model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"

# 임베딩 모델 로드 (HuggingFaceEmbeddings 사용)
embedding_model = HuggingFaceEmbeddings(model_name=model_name)

# 특정 컬렉션 삭제 및 새로운 컬렉션 생성
# delete_collection("case-law2")

# 디버깅 로그 추가: create_collection 호출 전
logger.info(f"create_collection 호출 전: embedding_model={embedding_model}")
collection = create_collection("case-law2", embedding_model)

# 텍스트 임베딩 생성 및 벡터 데이터베이스에 저장 함수 정의
def embed_and_store_documents(docs):
    chunked_docs = get_text_chunks(docs)
    if chunked_docs is None:
        return {"message": "텍스트 청크 처리 실패"}

    texts = [doc.page_content for doc in chunked_docs]
    metadatas = [doc.metadata for doc in chunked_docs]

    # HuggingFace 임베딩을 사용하여 의미론적 청크 분할기를 초기화합니다.
    text_splitter = SemanticChunker(embedding_model)

    # 텍스트를 의미론적으로 관련된 청크로 분할합니다.
    logger.info("텍스트 의미론적 청크 분할 시작...")
    try:
        chunks = text_splitter.split_text(" ".join(texts))
        logger.info(f"텍스트 의미론적 청크 분할 완료, 생성된 청크 수: {len(chunks)}")
    except Exception as e:
        logger.error(f"텍스트 의미론적 청크 분할 실패: {e}")
        return {"message": "텍스트 의미론적 청크 분할 실패"}

    # Chroma 벡터 데이터베이스에 문서 추가
    try:
        logger.info("벡터 DB 저장중입니다...")
        ids = [f"case-{i}" for i in range(len(chunks))]
        collection.add_texts(
            texts=chunks,
            metadatas=metadatas,
            ids=ids
        )
        logger.info("벡터 데이터베이스에 저장 성공")
    except Exception as e:
        logger.error(f"벡터 데이터베이스에 저장 실패: {e}")
        return {"message": "벡터 데이터베이스에 저장 실패"}

    return {"message": "ChromaDB에 저장되었습니다.", "num_documents": len(chunked_docs)}
