# 4 임베딩 및 저장 모듈
# 이 모듈은 텍스트 임베딩을 생성하고, 벡터 데이터베이스에 저장하는 기능을 제공합
# 임베딩 모델을 사용해 텍스트를 벡터로 변환하고 ChromaDB에 저장

from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
import logging
from .data_processing import get_text_chunks

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 임베딩 모델 로드 (SentenceTransformerEmbeddings 사용)
embedding_model = SentenceTransformerEmbeddings(model_name='paraphrase-MiniLM-L6-v2')

# 사용 가능한 메서드와 속성 출력
# print(dir(embedding_model))

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
        # aembed_documents 메서드를 사용하여 임베딩 생성
        embeddings = embedding_model.aembed_documents(texts)
        if embeddings is None or len(embeddings) == 0:
            raise ValueError("임베딩 생성 실패")
        logger.info(f"임베딩 모델 함수 호출 완료, 생성된 임베딩 수: {len(embeddings)}")
    except Exception as e:
        logger.error(f"임베딩 모델 함수 호출 실패: {e}")
        return {"message": "임베딩 생성 실패"}

    # Chroma 벡터 데이터베이스에 문서 추가
    try:
        logger.info("벡터 DB 저장중입니다...")
        # Chroma 객체를 초기화할 때 embedding_function 인자를 추가하여 임베딩 함수를 제공
        vectorstore = Chroma(collection_name="case-law2", embedding_function=embedding_model.aembed_documents)
        ids = [f"case-{i}" for i in range(len(texts))]
        vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids, embeddings=embeddings)
        logger.info("벡터 데이터베이스에 저장 성공")
    except Exception as e:
        logger.error(f"벡터 데이터베이스에 저장 실패: {e}")
        return {"message": "벡터 데이터베이스에 저장 실패"}

    return {"message": "ChromaDB에 저장되었습니다.", "num_documents": len(chunked_docs)}
