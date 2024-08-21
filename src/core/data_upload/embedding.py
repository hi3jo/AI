import logging
import os
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from .chroma_db import delete_collection, create_collection
from .data_processing import get_text_chunks
from dotenv import load_dotenv

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

# HuggingFace 모델 이름 설정
model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"

# 임베딩 모델 로드 (HuggingFaceEmbeddings 사용)
embedding_model = HuggingFaceEmbeddings(model_name=model_name)

# 특정 컬렉션 삭제 및 새로운 컬렉션 생성
delete_collection("case-law2")

# 디버깅 로그 추가: create_collection 호출 전
logger.info(f"create_collection 호출 전: embedding_model={embedding_model}")
collection = create_collection("case-law2", embedding_model)

# 텍스트 임베딩 생성 및 벡터 데이터베이스에 저장 함수 정의
def embed_and_store_documents(docs):
    try:
        # 최종 청크(의미론적 + 더 작게) 생성
        chunked_docs = get_text_chunks(docs)
        if chunked_docs is None:
            raise ValueError("텍스트 청크 처리 실패")

        # 각 청크에서 텍스트와 메타데이터를 추출
        texts = [doc.page_content for doc in chunked_docs]
        metadatas = [doc.metadata for doc in chunked_docs]

         # 데이터 검증 (추가적인 데이터 검증 단계)
        logger.info(f"텍스트 개수: {len(texts)}, 메타데이터 개수: {len(metadatas)}, ID 개수: {len(chunked_docs)}")
        if len(texts) == 0 or len(metadatas) == 0 or len(chunked_docs) == 0:
            logger.error("텍스트, 메타데이터 또는 ID가 비어 있습니다.")
            return {"message": "데이터가 비어 있습니다."}

        # 데이터 검증 (예외 처리 강화)
        # if len(texts) != len(metadatas):
        #     raise ValueError("텍스트와 메타데이터의 길이가 일치하지 않습니다.")

        # Chroma 벡터 데이터베이스에 문서 추가
        try:
            logger.info("벡터 DB 저장중...")
            ids = [f"case-{i}" for i in range(len(texts))]
            
            # 추가 디버깅 로그
            logger.debug(f"texts: {texts[:10]}")  # 첫 5개 텍스트만 로그에 기록 (길면 생략)
            logger.debug(f"metadatas: {metadatas[:10]}")
            logger.debug(f"ids: {ids[:10]}")
            
            # 함수 실행 시간을 측정하기 위한 추가 코드
            # import time
            # start_time = time.time()
            
            try:
                collection.add_texts(
                    texts=texts,
                    metadatas=metadatas,
                    ids=ids
                )
            except Exception as e:
                logger.error(f"collection.add_texts 실행 중 예외 발생: {e}")
                raise e
            
            logger.info(f"collection.add_texts 호출 완료 - 실행 시간: {time.time() - start_time}초")
            logger.info("벡터 데이터베이스에 저장 성공")
        except Exception as e:
            logger.error(f"벡터 데이터베이스에 저장 실패: {e}")
            return {"message": "벡터 데이터베이스에 저장 실패"}

        return {"message": "ChromaDB에 저장되었습니다.", "num_documents": len(chunked_docs)}
    
    except ValueError as ve:
        logger.error(f"데이터 처리 중 오류 발생: {ve}")
        return {"message": str(ve)}
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        return {"message": "예상치 못한 오류 발생"}
