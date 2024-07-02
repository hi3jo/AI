import pandas as pd
import chromadb
from langchain.embeddings import HuggingFaceEmbeddings

# 절대 경로 설정
DB_PATH = r"C:\ai\adventurer\AI\src\database\chatDB\chroma.sqlite3"

# 벡터 DB 로드 함수
def load_vector_db():
    try:
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        collection = chroma_client.get_or_create_collection(name="divorce_precedent")
        print("벡터 데이터베이스 로드 성공")
        return collection
    except Exception as e:
        print(f"벡터 데이터베이스 로드 실패: {e}")
        return None

# 임베딩 모델 생성 함수
def get_embeddings():
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("임베딩 모델 생성 성공")
        return embeddings
    except Exception as e:
        print(f"임베딩 모델 생성 실패: {e}")
        return None

# 문서 검색 함수
def search_vectorstore(query_text, num_results=10):
    
    #print("1.query_text", query_text)
    #print("2.num_results", num_results)
    embeddings = get_embeddings()
    if embeddings is None:
        print("임베딩 모델을 로드할 수 없습니다.")
        return None
    
    print("3.embeddings", embeddings)
    query_embedding = embeddings.embed_documents([query_text])[0]
    print("4.query_embedding", query_embedding)
    collection = load_vector_db()
    if collection is None:
        print("벡터 데이터베이스를 로드할 수 없습니다.")
        return None
    
    #print("5.collection", collection)
    #print("[query_embedding]", [query_embedding])
    #print("[num_results]", [num_results])

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=num_results
        )
        print("문서 검색 성공 : ", results)
        return results
    except Exception as e:
        print(f"문서 검색 실패: {e}")
        return None

# 메인 함수
def main():
    
    #쿼리 예시
    #query_text = '유서의 내용 중에는 피해자의 진술 등과 명백히 배치되는 부분도 존재한다.'
    print("메인 탔어?")
    query_text = '남편의 외도로 인하여'
    results = search_vectorstore(query_text)
    if results is None:
        print("문서 검색을 수행할 수 없습니다.")
        return
    
    print('검색 결과:', results)

if __name__ == '__main__':
    main()