# 2 ChromaDB 클라이언트 모듈
# ChromaDB 클라이언트 초기화 및 유사 문서 검색 함수 정의

import chromadb
# from langchain_community.vectorstores import Chroma
from src.core.chatbot.embeddings import ko_embedding
import logging

logger = logging.getLogger(__name__)

# ChromaDB 클라이언트 및 컬렉션 초기화 함수
def get_chroma_client():
    client = chromadb.PersistentClient(path="./data")
    collection = client.get_or_create_collection(name="case-law2", metadata={"hnsw:space": "cosine"})
    return collection

# ChromaDB 클라이언트 및 컬렉션 초기화 함수
# def get_chroma_client():
#     persist_directory = "./data"
    
#     try:
#         # Chroma 객체 초기화
#         chroma_client = Chroma(persist_directory=persist_directory, embedding_function=ko_embedding.embed_query)
#         logger.info("Chroma 객체를 성공적으로 초기화했습니다.")
#     except Exception as e:
#         logger.error(f"Chroma 객체를 초기화하는 데 실패했습니다: {e}")
#         raise ValueError("Chroma 객체를 초기화할 수 없습니다.")

#     return chroma_client

# 쿼리를 벡터화하여 유사한 문서 검색 함수 정의
def search_similar_documents(query, collection, num_results=5):
    query_embedding = ko_embedding.embed_query(query)
    logger.info(f"쿼리 임베딩 생성 완료: {query_embedding}")
    results = collection.query(query_embeddings=[query_embedding], n_results=num_results, include=["documents", "distances", "metadatas"])
    logger.info(f"유사한 문서 검색 결과: {results}")
    return results

# 데이터 검색을 위한 Retriever 함수 추가
def chroma_retriever(query, collection, embeddings):
    try:
        query_embedding = embeddings.encode(query, convert_to_tensor=False)
        results = collection.query(query_embeddings=[query_embedding], n_results=3, include=["documents", "metadatas"])
        logger.info(f"Query 수행 성공, 결과 수: {len(results['documents'])}")
        return results["documents"], results["metadatas"]
    except Exception as e:
        logger.error(f"Query 수행 실패: {e}")
        return [], []

