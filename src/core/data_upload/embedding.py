from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import logging
from .chroma_db import collection, get_or_create_collection
from .data_processing import get_text_chunks

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 임베딩 모델 로드 (SentenceTransformerEmbeddings 사용)
embedding_model = SentenceTransformerEmbeddings(model_name='paraphrase-MiniLM-L6-v2')

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
        embeddings = embedding_model.embed_documents(texts)
        if embeddings is None or len(embeddings) == 0:
            raise ValueError("임베딩 생성 실패")
        logger.info(f"임베딩 모델 함수 호출 완료, 생성된 임베딩 수: {len(embeddings)}")
    except Exception as e:
        logger.error(f"임베딩 모델 함수 호출 실패: {e}")
        return {"message": "임베딩 생성 실패"}

    # Chroma 벡터 데이터베이스에 문서 추가
    try:
        logger.info("벡터 DB 저장중입니다...")
        # collection = get_or_create_collection("case-law2")
        ids = [f"case-{i}" for i in range(len(texts))]
        collection.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        logger.info("벡터 데이터베이스에 저장 성공")
    except Exception as e:
        logger.error(f"벡터 데이터베이스에 저장 실패: {e}")
        return {"message": "벡터 데이터베이스에 저장 실패"}

    return {"message": "ChromaDB에 저장되었습니다.", "num_documents": len(chunked_docs)}
