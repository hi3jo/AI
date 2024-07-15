# 5 API 엔드포인트 정의
# ChromaDB 클라이언트 및 검색 함수, OpenAI 클라이언트와의 통합 처리
# 클라이언트 요청을 처리하고 응답을 반환하는 엔드포인트 구현

import warnings
from fastapi import APIRouter, HTTPException, Query, Depends
import logging
from src.core.chatbot.chromadb_client import get_chroma_client, search_similar_documents
from src.core.chatbot.openai_client import classify_question, generate_response
from src.core.chatbot.utils import truncate_text, format_metadata_response

# 경고 메시지 무시
warnings.filterwarnings("ignore", category=FutureWarning)

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 쿼리 라우터 정의
router = APIRouter()

@router.get("/query-v3/")
async def query_chromadb(query_text: str = Query(..., description="유사한 문서를 검색할 쿼리 텍스트"), num_results: int = Query(5, description="검색할 유사 문서의 개수"), collection = Depends(get_chroma_client)):
    try:
        search_results = search_similar_documents(query_text, collection, num_results=num_results)
    except Exception as e:
        logger.error(f"문서 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="문서 검색 중 오류가 발생했습니다.")
    
    similar_docs = []
    distances = []
    metadata_list = []
    for doc, dist, metadata in zip(search_results['documents'][0], search_results['distances'][0], search_results['metadatas'][0]):
        similar_docs.append(doc)
        distances.append(dist)
        metadata_list.append(metadata)
        logger.info(f"추출된 메타데이터: {metadata}")

    if not similar_docs:
        return {
            "query": query_text,
            "results": [],
            "distances": [],
            "answer": "유사한 문서가 없습니다.",
            "most_similar_info": []
        }

    # 문서의 내용을 줄이기 위해 처음 몇 개의 문서만 사용
    max_docs_for_summary = 3
    truncated_docs = similar_docs[:max_docs_for_summary]

    # 각 문서의 길이를 제한
    max_tokens_per_doc = 300
    truncated_docs = [truncate_text(doc, max_tokens_per_doc) for doc in truncated_docs]

    # 질문 타입 분류 및 응답 생성
    try:
        classified_question = classify_question(query_text)
        final_response = generate_response(query_text, classified_question['question_type'])
    except Exception as e:
        logger.error(f"OpenAI 응답 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="질문 분류 중 오류가 발생했습니다.")

    # 가장 유사한 판례의 메타데이터 추출 (최대 2개)
    most_similar_metadata = metadata_list[:2] if metadata_list else []
    most_similar_info = [
        {
            "법원명": metadata.get("법원명", "없음"),
            "사건번호": metadata.get("사건번호", "없음"),
            "판결요지": metadata.get("판결요지", "없음")
        }
        for metadata in most_similar_metadata
    ]

    return {
        "query": query_text,
        "results": similar_docs,
        "distances": distances,
        "answer": final_response,
        "most_similar_info": most_similar_info,
        "question_classification": classified_question
    }

# query_router 정의
query_router_v4 = router
