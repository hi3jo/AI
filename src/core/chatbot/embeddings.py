# 1 임베딩 모듈
# HuggingFace 임베딩 모델 초기화

from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# 텍스트 임베딩 모델 초기화
model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"
encode_kwargs = {'normalize_embeddings': True}
ko_embedding = HuggingFaceEmbeddings(
    model_name=model_name,
    encode_kwargs=encode_kwargs
)
