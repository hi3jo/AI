import logging
import os
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from .chroma_db import delete_collection, create_collection
from .data_processing import get_text_chunks
from dotenv import load_dotenv
import time
import psutil # 메모리 사용량, CPU 사용량 확인

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


# 현재 시스템의 메모리와 CPU 사용량을 로그에 기록하는 함수
def log_system_resources():
    process = psutil.Process(os.getpid())  # 현재 프로세스의 정보 가져오기
    mem_info = process.memory_info()  # 현재 프로세스의 메모리 사용량 정보 가져오기
    cpu_usage = psutil.cpu_percent(interval=1)  # 1초간의 CPU 사용량 계산
    
    # 메모리 사용량과 CPU 사용량을 로그로 출력
    logger.info(f"Memory Usage: {mem_info.rss / 1024 ** 2:.2f} MB")  # RSS 메모리 사용량 MB 단위로 기록
    logger.info(f"CPU Usage: {cpu_usage}%")  # CPU 사용량 기록

# 텍스트 임베딩을 생성하고 벡터 데이터베이스에 저장하는 함수
def embed_and_store_documents(docs, batch_size=2):
    try:
        # 문서 텍스트를 청크 단위로 나눕니다.
        chunked_docs = get_text_chunks(docs)
        if chunked_docs is None:
            raise ValueError("텍스트 청크 처리 실패")

        # 각 청크에서 텍스트와 메타데이터를 추출
        texts = [doc.page_content for doc in chunked_docs]
        metadatas = [doc.metadata for doc in chunked_docs]

        # 텍스트, 메타데이터, ID 개수 확인을 위한 로그
        logger.info(f"텍스트 개수: {len(texts)}, 메타데이터 개수: {len(metadatas)}, ID 개수: {len(chunked_docs)}")
        if len(texts) == 0 or len(metadatas) == 0 or len(chunked_docs) == 0:
            logger.error("텍스트, 메타데이터 또는 ID가 비어 있습니다.")
            return {"message": "데이터가 비어 있습니다."}

        # 각 텍스트 청크에 고유한 ID 할당
        ids = [f"case-{i}" for i in range(len(texts))]

        # 컬렉션 객체의 상태를 로그에 기록하여 확인
        logger.info(f"Collection object: {collection}")

        # 데이터를 배치 단위로 처리하여 메모리 사용량 최적화
        for i in range(0, len(texts), batch_size):
            # 현재 배치에서 처리할 텍스트, 메타데이터, ID 추출
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]

            try:
                logger.info(f"{i}-{i+batch_size}번째 배치 저장 중...")  # 현재 처리 중인 배치에 대한 로그
                
                # 시스템 리소스 상태 확인을 위한 로그 기록
                log_system_resources()

                # 배치에 포함된 텍스트, 메타데이터, ID를 로그에 출력
                logger.info(f"batch_texts: {batch_texts}")
                logger.info(f"batch_metadatas: {batch_metadatas}")
                logger.info(f"batch_ids: {batch_ids}")
                

                # `collection.add_texts` 함수 호출 전 로그 기록
                logger.info("collection.add_texts 호출 전")
                start_time = time.time()  # 함수 호출 전 시간 기록

                # 텍스트, 메타데이터, ID를 벡터 데이터베이스에 추가
                collection.add_texts(
                    texts=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )

                # `collection.add_texts` 함수 호출 후 걸린 시간과 함께 로그 기록
                logger.info(f"collection.add_texts 호출 완료, 걸린 시간: {time.time() - start_time:.2f}초")
                

                
            except Exception as e:
                # 예외 발생 시 로그에 기록하고, 오류 메시지 반환
                logger.error(f"벡터 DB에 배치 저장 중 예외 발생: {e}")
                return {"message": "배치 저장 중 오류 발생"}

        # 모든 배치가 성공적으로 저장되었음을 로그에 기록하고, 결과 반환
        logger.info("모든 배치 저장 성공")
        return {"message": "ChromaDB에 저장되었습니다.", "num_documents": len(chunked_docs)}
    
    except ValueError as ve:
        # 텍스트 처리 중 발생한 오류를 로그에 기록하고, 오류 메시지 반환
        logger.error(f"데이터 처리 중 오류 발생: {ve}")
        return {"message": str(ve)}
    except Exception as e:
        # 예상치 못한 오류 발생 시 로그에 기록하고, 시스템 리소스 상태 기록 후 오류 메시지 반환
        logger.error(f"예상치 못한 오류 발생: {e}")
        log_system_resources()
        return {"message": "예상치 못한 오류 발생"}

# # 텍스트 임베딩 생성 및 벡터 데이터베이스에 저장 함수 정의
# def embed_and_store_documents(docs):
#     try:
#         # 최종 청크(의미론적 + 더 작게) 생성
#         chunked_docs = get_text_chunks(docs)
#         if chunked_docs is None:
#             raise ValueError("텍스트 청크 처리 실패")

#         # 각 청크에서 텍스트와 메타데이터를 추출
#         texts = [doc.page_content for doc in chunked_docs]
#         metadatas = [doc.metadata for doc in chunked_docs]

#         # 데이터 검증 (추가적인 데이터 검증 단계)
#         # logger.info(f"텍스트 개수: {len(texts)}, 메타데이터 개수: {len(metadatas)}, ID 개수: {len(chunked_docs)}")
#         # if len(texts) == 0 or len(metadatas) == 0 or len(chunked_docs) == 0:
#         #     logger.error("텍스트, 메타데이터 또는 ID가 비어 있습니다.")
#         #     return {"message": "데이터가 비어 있습니다."}

#         # Chroma 벡터 데이터베이스에 문서 추가
#         try:
#             logger.info("벡터 DB 저장중...")
#             ids = [f"case-{i}" for i in range(len(texts))]
            
#             # 추가 디버깅 로그
#             # logger.info(f"texts: {texts[:3]}") 
#             # logger.info(f"metadatas: {metadatas[:3]}")
#             # logger.info(f"ids: {ids[:3]}")
            
#             #데이터 검증 (추가적인 데이터 검증 단계)
#             logger.info(f"텍스트 개수: {len(texts)}, 메타데이터 개수: {len(metadatas)}, ID 개수: {len(chunked_docs)}")
#             if len(texts) == 0 or len(metadatas) == 0 or len(chunked_docs) == 0:
#                 logger.error("텍스트, 메타데이터 또는 ID가 비어 있습니다.")
#                 return {"message": "데이터가 비어 있습니다."}
            
#             # 함수 실행 시간을 측정하기 위한 추가 코드
#             # import time
#             # start_time = time.time()
            
#             try:
#                 collection.add_texts(
#                     texts=texts,
#                     metadatas=metadatas,
#                     ids=ids
#                 )
#             except Exception as e:
#                 logger.error(f"collection.add_texts 실행 중 예외 발생: {e}")
#                 raise e
            
#             # logger.info(f"collection.add_texts 호출 완료 - 실행 시간: {time.time() - start_time}초")
#             logger.info("벡터 데이터베이스에 저장 성공")
#         except Exception as e:
#             logger.error(f"벡터 데이터베이스에 저장 실패: {e}")
#             return {"message": "벡터 데이터베이스에 저장 실패"}

#         return {"message": "ChromaDB에 저장되었습니다.", "num_documents": len(chunked_docs)}
    
#     except ValueError as ve:
#         logger.error(f"데이터 처리 중 오류 발생: {ve}")
#         return {"message": str(ve)}
#     except Exception as e:
#         logger.error(f"예상치 못한 오류 발생: {e}")
#         return {"message": "예상치 못한 오류 발생"}