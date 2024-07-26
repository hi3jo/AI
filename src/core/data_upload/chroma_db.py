from langchain_community.vectorstores import Chroma
import logging

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 기존 컬렉션 삭제 함수
def delete_collection(collection_name):
    try:
        logger.info(f"컬렉션 '{collection_name}' 삭제 시작")
        client = Chroma(collection_name=collection_name)
        client.delete_collection()
        logger.info(f"컬렉션 '{collection_name}' 삭제 성공")
    except Exception as e:
        logger.error(f"컬렉션 삭제 실패: {e}")

# ChromaDB 클라이언트 초기화 및 컬렉션 생성 함수
def create_collection(collection_name, embedding_function):
    try:
        logger.info(f"컬렉션 '{collection_name}' 생성 시작")
        collection = Chroma(collection_name=collection_name, embedding_function=embedding_function)
        logger.info(f"컬렉션 '{collection_name}' 생성 성공")
    except Exception as e:
        logger.error(f"컬렉션 생성 실패: {e}")
        collection = None
    
    return collection
