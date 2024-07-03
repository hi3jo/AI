import pandas as pd
import chromadb
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# 3.1.벡터 DB 로드 함수
def load_vector_db():
    
    try:
        
        chroma_client = chromadb.PersistentClient(path="./chroma.sqlite3")
        collection    = chroma_client.get_or_create_collection(name="divorce_precedent")
        print("벡터 데이터베이스 로드 성공")
        return collection
    except Exception as e:
        print(f"벡터 데이터베이스 로드 실패: {e}")
        return None

# 1. CSV 데이터 로드 함수
def load_csv_data():
    
    try:
        df = pd.read_csv('data.csv')
        documents = []
        for index, row in df.iterrows():
            #print(f"Index: {index}")  # 인덱스 출력
            판례일련번호 = str(row['판례일련번호'])
            판례내용     = str(row['판례내용'])
            #print(f"판례일련번호: {판례일련번호}")  # 판례일련번호 출력
            #print(f"판례내용: {판례내용}")  # 판례일련번호 출력
            documents.append(Document(page_content=row['판례내용'], metadata={"id": 판례일련번호}))
        print("CSV 데이터 로드 성공")
        return documents
    except Exception as e:
        print(f"CSV 데이터 로드 실패: {e}")
        return None

# 텍스트 길이 계산 함수
def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)

# 2. 텍스트 청크 처리 함수
def get_text_chunks(documents):
    
    all_chunks = []
    for index, doc in enumerate(documents):
        content = doc.page_content
        print("청크 대상 순번 :", index)
        #print("청크 대상 판례 아이디:", doc.metadata['id'])
        #print("청크 대상 판례:", doc.page_content)


        try:
            text_splitter = RecursiveCharacterTextSplitter(
                  chunk_size=100
                , chunk_overlap=20
                , length_function=tiktoken_len
            )
            # 개별 판례 사례를 청크 처리
            chunks = text_splitter.split_documents([doc])
            #print("청크 처리된 결과 :", chunks)
            for chunk_index, chunk in enumerate(chunks):
                print("꼭 확인 chunk :", chunk)
                all_chunks.extend(chunk)
        except Exception as e:
            print(f"텍스트 청크 처리 실패 (판례 아이디: {doc.metadata['id']}): {e}")
    
    return
    for index, chunk in enumerate(all_chunks):
        print("index :", index)
        print(f"청크 {index} 결과:")
        print("")  # 청크 사이에 빈 줄 추가

    return all_chunks if all_chunks else None

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

# 벡터 스토어 생성 및 데이터 저장 함수
def save_to_vectorstore(text_chunks):
    
    embeddings = get_embeddings()
    if embeddings is None:
        print("임베딩 모델을 로드할 수 없습니다.")
        return None

    collection = load_vector_db()
    if collection is None:
        print("벡터 데이터베이스를 로드할 수 없습니다.")
        return None

    try:
        
        for i, chunk in enumerate(text_chunks):
            
            print("for문 :", i)
            chunk_id = f"doc_{i}_{chunk.metadata['id']}"
            embedding = embeddings.embed_documents([chunk.page_content])[0]

            print("1.[chunk.page_content, 텍스트 데이터] : ", [chunk.page_content])
            collection.add(
                ids=[chunk_id]
                ,documents=[chunk.page_content]
                ,metadatas=[{  "chunk_id": chunk_id
                             , "case_id" : chunk.metadata['id']}]
                ,embeddings=[embedding]
            )
        print("벡터 스토어 저장 성공")
        return collection
    except Exception as e:
        print(f"벡터 스토어 저장 실패: {e}")
        return None

# 메인 함수
def main():
    
    # 1. 저장할 데이터를 가지고 있는 csv파일을 메모리에 적재한다.
    documents = load_csv_data()
    if documents is None:
        print("CSV 데이터를 로드할 수 없습니다.")
        return

    # 2. 데이터를 작업하기 쉽게 분할하고 묶는다.  
    text_chunks = get_text_chunks(documents)
    if text_chunks is None:
        print("텍스트 청크를 처리할 수 없습니다.")
        return


    # 3. 벡터 DB로 데이터를 insert 한다.
    vectorstore = save_to_vectorstore(text_chunks)
    if vectorstore is None:
        print("벡터 스토어를 생성할 수 없습니다.")
        return

    print('VectorDB로 csv내 데이터 저장 완료!')

if __name__ == '__main__':
    main()