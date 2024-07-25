import logging
from langchain_community.vectorstores import Chroma

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 기존 컬렉션 삭제 함수
def delete_collection(collection_name):
    try:
        logger.info(f"컬렉션 '{collection_name}' 삭제 시작")
        # Chroma 인스턴스를 초기화하여 특정 컬렉션을 삭제
        client = Chroma(collection_name=collection_name)
        client.delete_collection()
        logger.info(f"컬렉션 '{collection_name}' 삭제 성공")
    except Exception as e:
        logger.error(f"컬렉션 삭제 실패: {e}")

# ChromaDB 클라이언트 초기화 및 컬렉션 생성/가져오기 함수
def get_or_create_collection(collection_name):
    try:
        logger.info(f"컬렉션 '{collection_name}' 생성 또는 가져오기 시작")
        collection = Chroma(collection_name=collection_name)
        logger.info(f"컬렉션 '{collection_name}' 가져오기 또는 생성 성공")
    except Exception as e:
        logger.error(f"컬렉션 가져오기 또는 생성 실패: {e}")
        collection = None
    
    return collection

# 특정 컬렉션 삭제
delete_collection("case-law2")

# 새로운 컬렉션 생성
collection = get_or_create_collection("case-law2")
