import chromadb

# PersistentClient 생성
chroma_client = chromadb.PersistentClient(path="./chroma.sqlite3")

# divorce_precedent 컬렉션 가져오기
collection = chroma_client.get_or_create_collection(name="divorce_precedent")

# 데이터 개수 확인
count = collection.count()
print(f"divorce_precedent 컬렉션에 있는 데이터 개수: {count}")