import pandas as pd
import chromadb
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# 1. 벡터 DB 로드 함수
def loadVectorDB():
    chroma_client = chromadb.PersistentClient(path="./chroma.sqlite3")
    collection = chroma_client.get_or_create_collection(name="divorce_precedent")
    return collection

# CSV 데이터 로드 함수
def loadCsvData():
    df = pd.read_csv('crawling2024.csv')
    documents = []
    for index, row in df.iterrows():
        id = str(row['판례일련번호'])
        document = row['판례내용']
        documents.append(Document(page_content=document, metadata={"id": id}))
        
        #print("asdf", document)
        
    return documents

# 텍스트 길이 계산 함수
def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)

# 텍스트 청크 처리 함수
def get_text_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=100,
        length_function=tiktoken_len
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

# 임베딩 모델 생성 함수
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

# 벡터 스토어 생성 및 데이터 저장 함수
def get_vectorstore(text_chunks):
    embeddings = get_embeddings()
    collection = loadVectorDB()
    
    print(1)
    for i, chunk in enumerate(text_chunks):
        print(2)
        print("Asdfasdfsadf",[chunk.page_content])
        embedding = embeddings.embed_documents([chunk.page_content])
        collection.add(
            ids=[f"doc_{i}"],
            documents=[chunk.page_content],
            metadatas=[{"chunk_id": i}],
            embeddings=embedding[0]  # embedding[0]으로 단일 벡터를 전달
        )
    
    return collection

# 벡터 스토어에서 데이터 조회 함수
def query_vectorstore(query_text):
    embeddings = get_embeddings()
    query_embedding = embeddings.embed_documents([query_text])[0]
    collection = loadVectorDB()
    
    # 유사한 문서 검색
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,  # 원하는 결과 개수
        include=["documents", "metadatas", "distances"]
    )
    
    return results

# 메인 함수
def main():
    
    documents = loadCsvData()
    text_chunks = get_text_chunks(documents)
    print("text_chunks : ", text_chunks)
    vectorstore = get_vectorstore(text_chunks)
    print('벡터 스토어 저장 완료: ', vectorstore)
    
    # 쿼리 예제
    # query_text = "이혼 판례에 대한 예시 텍스트"
    # results = query_vectorstore(query_text)
    
    # print("검색 결과: ", results)
    
    # # 검색 결과에서 텍스트 추출
    # if 'documents' in results and results['documents']:
    #     for i, doc in enumerate(results['documents'][0]):
    #         print(f"결과 {i+1}: ", doc)
if __name__ == '__main__':
    main()