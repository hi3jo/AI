# 2 ChromaDB 관리 모듈
# 이 모듈은 ChromaDB 클라이언트를 초기화하고,
# 컬렉션을 생성하거나 가져오는 기능을 제공합니다.

import logging
import chromadb
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 임베딩 모델 로드 (SentenceTransformerEmbeddings 사용)
embedding_model = SentenceTransformerEmbeddings(model_name='paraphrase-MiniLM-L6-v2')

# 기존 컬렉션 삭제 함수
def delete_collection(collection_name):
    try:
        logger.info(f"컬렉션 '{collection_name}' 삭제 시작")
        # Chroma 인스턴스를 초기화하여 특정 컬렉션을 삭제
        client = Chroma(collection_name=collection_name, embedding_function=embedding_model.embed_documents)
        client.delete()
        logger.info(f"컬렉션 '{collection_name}' 삭제 성공")
    except Exception as e:
        logger.error(f"컬렉션 삭제 실패: {e}")

# ChromaDB 클라이언트 초기화 및 컬렉션 생성/가져오기 함수
def get_or_create_collection(collection_name):
    try:
        logger.info(f"컬렉션 '{collection_name}' 생성 또는 가져오기 시작")
        collection = Chroma(collection_name=collection_name, embedding_function=embedding_model.embed_documents)
        logger.info(f"컬렉션 '{collection_name}' 가져오기 또는 생성 성공")
    except Exception as e:
        logger.error(f"컬렉션 가져오기 또는 생성 실패: {e}")
        collection = None
    
    return collection

# case-law2 컬렉션 삭제
delete_collection("case-law2")

# 새로운 컬렉션 생성
collection = get_or_create_collection("case-law2")
