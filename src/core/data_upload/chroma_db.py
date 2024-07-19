# 2 ChromaDB 관리 모듈
# 이 모듈은 ChromaDB 클라이언트를 초기화하고,
# 컬렉션을 생성하거나 가져오는 기능을 제공합니다.

import chromadb
import logging

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ChromaDB 클라이언트 초기화
client = chromadb.PersistentClient(path="./data")

# 컬렉션 삭제
# def delete_collection(client, collection_name):
#     try:
#         client.delete_collection(name=collection_name)
#         logger.info(f"컬렉션 '{collection_name}' 삭제 성공")
#     except Exception as e:
#         logger.error(f"컬렉션 삭제 실패: {e}")

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

# 기존 컬렉션 삭제
# delete_collection(client, "case-law3")
# delete_collection(client, "case-law")

# 새로운 컬렉션 생성
collection = get_or_create_collection(client, "case-law2")
