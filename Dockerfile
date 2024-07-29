# webhook 테스트
# 베이스 이미지로 Python 3.12.4 사용(24/07/29, Runner 미사용, 젠킨스만)
FROM python:3.12.4

# 작업 디렉토리 생성 및 설정
RUN mkdir -p /app
WORKDIR /app

# 프로젝트 파일 추가
ADD . /app/

# 필요하다면, 종속성 파일 제거 (해당 사항 없으면 삭제 가능, 만들지 않고 직접 올린 것으로 실행할 것임)
# RUN rm -f requirements.txt

# 종속성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 환경 변수 설정
ENV HOST 0.0.0.0
ENV PORT 8000

# 포트 노출
EXPOSE 8000

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
