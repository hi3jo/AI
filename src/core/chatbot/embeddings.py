# 1 임베딩 모듈
# HuggingFace 임베딩 모델 초기화

from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# 텍스트 임베딩 모델 초기화
model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"
encode_kwargs = {'normalize_embeddings': True}
# ko_embedding 모델은 사용자가 입력한 질문이나 문서를 벡터 형태로 변환하여,
# 유사한 문서를 검색할 수 있도록 도와줌
ko_embedding = HuggingFaceEmbeddings(
    model_name=model_name,
    encode_kwargs=encode_kwargs
)
