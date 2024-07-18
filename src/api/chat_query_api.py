import warnings
from fastapi import APIRouter, HTTPException, Query, Depends
import logging
from src.core.chatbot.chromadb_client import get_chroma_client, search_similar_documents
from src.core.chatbot.openai_client import classify_question, generate_response, chat_history
from src.core.chatbot.utils import truncate_text, format_metadata_response

# 경고 메시지 무시
warnings.filterwarnings("ignore", category=FutureWarning)

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 쿼리 라우터 정의
router = APIRouter()

# 첫 번째 인터랙션을 확인하는 플래그
# 첫 번째 질문-답변 시 추가 정보를 저장합니다.
first_interaction = True

# /query-v3/ 엔드포인트 정의
@router.get("/query-v3/")
async def query_chromadb(query_text: str = Query(..., description="유사한 문서를 검색할 쿼리 텍스트"), num_results: int = Query(5, description="검색할 유사 문서의 개수"), collection = Depends(get_chroma_client)):
    global first_interaction
    
    try:
        # ChromaDB에서 유사한 문서를 검색
        search_results = search_similar_documents(query_text, collection, num_results=num_results)
    except Exception as e:
        # 오류 발생 시 로그에 기록하고 500 오류 반환
        logger.error(f"문서 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="문서 검색 중 오류가 발생했습니다.")
    
    similar_docs = []
    distances = []
    metadata_list = []
    # 검색 결과에서 문서, 거리 및 메타데이터 추출
    for doc, dist, metadata in zip(search_results['documents'][0], search_results['distances'][0], search_results['metadatas'][0]):
        similar_docs.append(doc)
        distances.append(dist)
        metadata_list.append(metadata)
        logger.info(f"추출된 메타데이터: {metadata}")

    # 유사한 문서가 없는 경우
    if not similar_docs:
        return {
            "query": query_text,
            "results": [],
            "distances": [],
            "answer": "유사한 문서가 없습니다.",
            "most_similar_info": []
        }

    # 문서 요약을 위해 처음 몇 개의 문서만 사용
    max_docs_for_summary = 3
    truncated_docs = similar_docs[:max_docs_for_summary]
    max_tokens_per_doc = 300
    truncated_docs = [truncate_text(doc, max_tokens_per_doc) for doc in truncated_docs]

    try:
        # 질문 유형 분류
        classified_question = classify_question(query_text)
        most_similar_metadata = metadata_list[:2] if metadata_list else []
        most_similar_info = [
            {
                "법원명": metadata.get("법원명", "없음"),
                "사건번호": metadata.get("사건번호", "없음"),
                "판결요지": metadata.get("판결요지", "없음")
            }
            for metadata in most_similar_metadata
        ]
        # 응답 생성
        final_response = generate_response(query_text, classified_question['question_type'], chat_history, first_interaction, similar_docs, most_similar_info)
    except Exception as e:
        # 오류 발생 시 로그에 기록하고 500 오류 반환
        logger.error(f"OpenAI 응답 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="질문 분류 중 오류가 발생했습니다.")

    # 대화기록에 질문과 분류된 질문 유형 추가
    chat_history.add_message({"role": "user", "content": query_text})
    chat_history.add_message({"role": "assistant", "content": f"Classified question type: {classified_question['question_type']}"})
    chat_history.add_message({"role": "assistant", "content": final_response})

    # 첫 번째 인터랙션일 경우 추가 정보 저장
    if first_interaction:
        chat_history.add_message({"role": "system", "content": f"Results: {similar_docs}"})
        chat_history.add_message({"role": "system", "content": f"Most similar info: {most_similar_info}"})
        first_interaction = False

    # 대화 기록 로그에 기록
    logger.info(f"대화 기록 업데이트: {chat_history.messages}")

    # 응답 반환
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
