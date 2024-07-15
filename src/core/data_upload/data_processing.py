# 3 데이터 처리 모듈
# 이 모듈은 CSV 파일을 로드하고 텍스트를 청크로 분리하는 기능 제공

import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging

# 로그 설정
logger = logging.getLogger(__name__)

# 텍스트 길이 계산 함수
def tiktoken_len(text):
    return len(text)

# CSV 파일 로드 및 텍스트 청크 생성 함수 정의
def load_csv(file_path):
    try:
        # 잘못된 행 건너뛰기
        df = pd.read_csv(file_path, on_bad_lines='skip')
        docs = []
        for _, row in df.iterrows():
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
        logger.info("CSV 파일 로드 성공")
        return docs
    except Exception as e:
        logger.error(f"CSV 파일 로드 실패: {e}")
        return None

# 텍스트 청크 생성 함수 정의
def get_text_chunks(documents):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=tiktoken_len
        )
        chunks = text_splitter.split_documents(documents)
        logger.info("텍스트 청크 처리 성공")
        return chunks
    except Exception as e:
        logger.error(f"텍스트 청크 처리 실패: {e}")
        return None
