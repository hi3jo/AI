# 3 데이터 처리 모듈
# 이 모듈은 CSV 파일을 로드하고 텍스트를 청크로 분리하는 기능 제공

import re
import logging
import os
from typing import List, Optional
import pandas as pd
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

# HuggingFace 모델 이름 설정
model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 텍스트 길이 계산 함수
def tiktoken_len(text):
    return len(text)


# PDF 파일을 로드하여 텍스트를 추출하고 청크를 생성하는 함수
def load_pdf(file_path):
    try:
        logger.info(f"PDF 파일 로드 시작: {file_path}")
        reader = PdfReader(file_path)
        docs = []
        for i, page in enumerate(reader.pages):
            # 각 페이지의 텍스트를 추출
            text = page.extract_text()
            if text:
                # Document 객체에 페이지 텍스트와 메타데이터 저장
                metadata = {"page_number": i + 1}
                docs.append(Document(page_content=text, metadata=metadata))
                logger.debug(f"문서 생성: 페이지 번호 {i + 1}")
        logger.info("파일 로드 성공")

        # 텍스트를 로드한 후 청크로 분할하여 반환
        return get_text_chunks(docs)
    except Exception as e:
        logger.error(f"파일 로드 실패: {e}")
        return None
    
# CSV 파일 로드 및 텍스트 청크 생성 함수 정의
def load_csv(file_path):
    try:
        logger.info(f"CSV 파일 로드 시작: {file_path}")
        # 잘못된 행 건너뛰기
        df = pd.read_csv(file_path, on_bad_lines='skip')
        docs = []
        for index, row in df.iterrows():
            # 판례내용과 메타데이터 저장
            text = row['판례내용']
            metadata = {
                "판례일련번호": row["판례일련번호"],
                "사건명": row.get("사건명", "없음"),
                "사건번호": row.get("사건번호", "없음"),
                "법원명": row.get("법원명", "없음"),
                "판결요지": row.get("판결요지", "없음")
            }
            docs.append(Document(page_content=text, metadata=metadata))
            logger.debug(f"문서 생성: {index}, 판례일련번호: {row['판례일련번호']}")
        logger.info("파일 로드 성공")
        return docs
    except Exception as e:
        logger.error(f"파일 로드 실패: {e}")
        return None

# SemanticChunkerWithMaxChunkLength 클래스 정의
class SemanticChunkerWithMaxChunkLength(SemanticChunker):
    def __init__(
        self,
        embeddings: HuggingFaceEmbeddings,
        add_start_index: bool = False,
        #  breakpoint_threshold_type과 breakpoint_threshold_amount는 SemanticChunker 클래스의 파라미터입니다.
        # 텍스트를 나눌 때 사용할 임계값의 유형을 지정
        breakpoint_threshold_type = "percentile",
        # 임계값의 구체적인 수치를 설정합니다.
        # 이 수치는 텍스트를 청크로 나누는 기준이 됩니다. 
        # 이 값이 낮을수록 더 작은 청크로 나눌 수 있습니다.
        breakpoint_threshold_amount: Optional[float] = 80.0,  # 더 작은 청크 생성, 기본값(파라미터)
        number_of_chunks: Optional[int] = None,
        max_chunk_length: Optional[int] = 1000,  # 최대 청크 크기, 기본값(파라미터)
    ):
        logger.info("SemanticChunkerWithMaxChunkLength 초기화 시작")
        # 상위 클래스(SemanticChunker)의 초기화 메소드를 호출하여 설정을 상속받음
        super().__init__(
            embeddings=embeddings,
            add_start_index=add_start_index,
            breakpoint_threshold_type=breakpoint_threshold_type,
            breakpoint_threshold_amount=breakpoint_threshold_amount,
            number_of_chunks=number_of_chunks,
        )
        self.max_chunk_length = max_chunk_length  # 추가로 청크의 최대 길이를 설정
        logger.info(f"SemanticChunkerWithMaxChunkLength 초기화 완료: max_chunk_length={self.max_chunk_length}")

    def split_text(
        self,
        text: str,
    ) -> List[str]:
        logger.info("텍스트 분할 시작")
        # 상위 클래스의 split_text 메소드를 호출하여 기본 청크 분할 수행
        chunks = super().split_text(text)

        # max_chunk_length가 설정되어 있지 않으면 기본 청크 반환
        if not self.max_chunk_length:
            logger.info(f"max_chunk_length가 설정되지 않아 기본 청크 반환, 청크 수: {len(chunks)}")
            return chunks

        # 청크 길이를 확인하고, max_chunk_length를 초과하는 경우 추가로 분할
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.max_chunk_length:
                logger.info(f"청크 길이 초과: {len(chunk)}, 추가 분할 진행")
                # 청크가 너무 크면 split_chunk_by_length 메소드를 사용해 분할
                final_chunks.extend(self.split_chunk_by_length(chunk))
            else:
                final_chunks.append(chunk)

        logger.info(f"최종 청크 분할 완료: 최종 청크 수={len(final_chunks)}")
        return final_chunks

    def split_chunk_by_length(self, chunk: str) -> List[str]:
        logger.info(f"청크 길이 초과로 추가 분할 시작: 청크 길이={len(chunk)}")
        # 주어진 청크를 문장 단위로 분할
        sentences = re.split(r"(?<=[.?!])\s+", chunk)
        new_chunks = []
        current_chunk = []

        # 문장 중 max_chunk_length를 초과하는 문장이 있는지 확인
        longer_sentence_length = max(len(sentence) for sentence in sentences)
        if longer_sentence_length > self.max_chunk_length:
            logger.error(
                f"청크 내 문장 길이 초과: 문장 길이={longer_sentence_length}, max_chunk_length={self.max_chunk_length}"
            )
            raise ValueError(
                f"Got a sentence longer than `max_chunk_length`: {longer_sentence_length}"
            )

        for sentence in sentences:
            # 현재 청크에 문장을 추가할 때 max_chunk_length를 초과하지 않는지 확인
            if len(' '.join(current_chunk + [sentence])) <= self.max_chunk_length:
                current_chunk.append(sentence)
            else:
                # 청크가 비어 있지 않다면 새로운 청크로 저장
                if current_chunk:
                    new_chunks.append(' '.join(current_chunk))
                # 새로운 청크 시작
                current_chunk = [sentence]

        # 마지막 청크가 남아있다면 저장
        if current_chunk:
            new_chunks.append(' '.join(current_chunk))

        logger.info(f"추가 분할 완료: 생성된 청크 수={len(new_chunks)}")
        return new_chunks

# 텍스트 청크 생성 함수 정의
def get_text_chunks(documents):
    try:
        logger.info("텍스트 청크 분할 시작")

        # 의미론적 청크 분할 (SemanticChunkerWithMaxChunkLength 사용)
        semantic_splitter = SemanticChunkerWithMaxChunkLength(
            embeddings=HuggingFaceEmbeddings(model_name=model_name),
            max_chunk_length=1500,  # 실제 적용 값, 최대 청크 길이 설정
            breakpoint_threshold_amount=70.0  #실제 적용 값, 청크 크기를 줄이기 위해 임계값 설정
        )
        
        # 의미론적 청크를 저장할 리스트 초기화
        semantic_chunks = []
        
        # 입력된 각 문서에 대해 반복 처리
        for doc in documents:
            # 문서 내용을 의미론적으로 분할하여 청크 리스트로 반환
            chunks = semantic_splitter.split_text(doc.page_content)
            
            # 각 청크를 Document 객체로 변환하여 metadata를 유지하며 리스트에 추가
            for chunk in chunks:
                semantic_chunks.append(Document(page_content=chunk, metadata=doc.metadata))
        
        # 의미론적 청크 분할이 완료되었음을 알리는 로그 메시지 (생성된 청크 수 포함)
        logger.info(f"의미론적 청크 분할 완료, 청크 수: {len(semantic_chunks)}")

        logger.info("텍스트 청크 처리 성공")
        print(semantic_chunks) # semantic_chunks 결과 확인 
        return semantic_chunks  # 최종적으로 의미론적으로 작은 청크를 반환
    
    # 분할 과정에서 발생할 수 있는 예외 처리
    except Exception as e:
        # 에러 발생 시 로그 메시지 출력 (에러 메시지 포함)
        logger.error(f"텍스트 청크 처리 실패: {e}")
        return None

