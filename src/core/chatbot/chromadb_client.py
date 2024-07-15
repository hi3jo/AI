# 2 ChromaDB 클라이언트 모듈
# ChromaDB 클라이언트 초기화 및 유사 문서 검색 함수 정의

import chromadb
from src.core.chatbot.embeddings import ko_embedding
import logging

logger = logging.getLogger(__name__)

# ChromaDB 클라이언트 및 컬렉션 초기화 함수
def get_chroma_client():
    client = chromadb.PersistentClient(path="./data")
    collection = client.get_or_create_collection(name="case-law3", metadata={"hnsw:space": "cosine"})
    return collection

# 쿼리를 벡터화하여 유사한 문서 검색 함수 정의
def search_similar_documents(query, collection, num_results=5):
    query_embedding = ko_embedding.embed_query(query)
    logger.info(f"쿼리 임베딩 생성 완료: {query_embedding}")
    results = collection.query(query_embeddings=[query_embedding], n_results=num_results, include=["documents", "distances", "metadatas"])
    logger.info(f"유사한 문서 검색 결과: {results}")
    return results
