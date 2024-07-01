import chromadb

# PersistentClient 생성
chroma_client = chromadb.PersistentClient(path="./chroma.sqlite3")

# divorce_precedent 컬렉션 가져오기
collection = chroma_client.get_or_create_collection(name="divorce_precedent")

# 데이터 개수 확인
count = collection.count()
print(f"divorce_precedent 컬렉션에 있는 데이터 개수: {count}")

#모든 데이터의 ID 가져오기
# all_data = collection.get(where={})
# all_ids = all_data.get('ids', [])

# # 모든 데이터 삭제
# if all_ids:
#     collection.delete(ids=all_ids)
#     print("divorce_precedent 컬렉션의 모든 데이터를 삭제했습니다.")
# else:
#     print("삭제할 데이터가 없습니다.")