import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticChunker:
    def __init__(self, model_name: str, max_chunk_length: int = 1000, threshold: float = 0.5):
        self.model = SentenceTransformer(model_name)
        self.max_chunk_length = max_chunk_length
        self.threshold = threshold

    def split_text(self, text: str):
        sentences = re.split(r"(?<=[.?!])\s+", text)
        embeddings = self.model.encode(sentences)
        
        chunks = []
        current_chunk = []
        current_length = 0

        for i in range(len(sentences)):
            if current_length + len(sentences[i]) <= self.max_chunk_length:
                current_chunk.append(sentences[i])
                current_length += len(sentences[i])
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentences[i]]
                current_length = len(sentences[i])

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        final_chunks = self._merge_similar_chunks(chunks, embeddings)
        return final_chunks

    def _merge_similar_chunks(self, chunks, embeddings):
        merged_chunks = []
        current_chunk = chunks[0]
        current_embedding = embeddings[0]

        for i in range(1, len(chunks)):
            sim = cosine_similarity([current_embedding], [embeddings[i]])[0][0]
            if sim > self.threshold:
                current_chunk += " " + chunks[i]
            else:
                merged_chunks.append(current_chunk)
                current_chunk = chunks[i]
                current_embedding = embeddings[i]

        merged_chunks.append(current_chunk)
        return merged_chunks

# 테스트할 법률 텍스트
text = """
제 1장 총칙 제1조(목적) 이 법은 공동주택의 관리에 관한 사항을 정함으로써 공동주택을 투명하고 안전하며 효율적으로 관리할 수 있게 하여
국민의 주거수준 향상에 이바지함을 목적으로 한다. 제2조(정의) ① 이 법에서 사용하는 용어의 뜻은 다음과 같다.
 <개정 2015. 8. 28., 2015. 12. 29., 2016. 1. 19., 2017. 4. 18., 2019. 4. 23.> 1. “공동주택”이란 다음 각 목의 주택 및 시설을 말한다. 
 이 경우 일반인에게 분양되는 복리시설은 제외한다. 가. 「주택법」 제2조제3호에 따른 공동주택 나. 「건축법」 제11조에 따른 건축허가를 받아 주택 외의 시설과 
 주택을 동일 건축물로 건축하는 건축물 다. 「주택법」 제2조제13호에 따른 부대시설 및 같은 조 제14호에 따른 복리시설 2. “의무관리대상 공동주택”이란
   해당 공동주택을 전문적으로 관리하는 자를 두고 자치 의결기구를 의무적으로 구성하여야 하는 등 일정한 의무가 부과되는 공동주택으로서, 다음 각 목 중
     어느 하나에 해당하는 공동주택을 말한다. 가. 300세대 이상의 공동주택 나. 150세대 이상으로서 승강기가 설치된 공동주택 다. 150세대 이상으로서 
     중앙집중식 난방방식(지역난방방식을 포함한다)의 공동주택 라. 「건축법」 제11조에 따른 건축허가를 받아 주택 외의 시설과 주택을 동일 건축물로
       건축한 건축물로서 주택이 150세대 이상인 건축물 마. 가목부터 라목까지에 해당하지 아니하는 공동주택 중 입주자등이 대통령령으로 정하는 기준에 따라 
       동의하여 정하는 공동주택 3. “공동주택단지”란 「주택법」 제2조제12호에 따른 주택단지를 말한다. 4. “혼합주택단지”란 분양을 목적으로 한 공동주택과 
       임대주택이 함께 있는 공동주택단지를 말한다. 5. “입주자”란 공동주택의 소유자 또는 그 소유자를 대리하는 배우자 및 직계존비속(直系尊卑屬)을 말한다.
         6. “사용자”란 공동주택을 임차하여 사용하는 사람(임대주택의 임차인은 제외한다) 등을 말한다. 7. “입주자등”이란 입주자와 사용자를 말한다. 
         8. “입주자대표회의”란 공동주택의 입주자등을 대표하여 관리에 관한 주요사항을 결정하기 위하여 제14조에 따라 구성하는 자치 의결기구를 말한다. 
         9. “관리규약”이란 공동주택의 입주자등을 보호하고 주거생활의 질서를 유지하기 위하여 제18조제2항에 따라 입주 자등이 정하는 자치규약을 말한다. 
         10. “관리주체”란 공동주택을 관리하는 다음 각 목의 자를 말한다. 가. 제6조제1항에 따른 자치관리기구의 대표자인 공동주택의 관리사무소장 
         나. 제13조제1항에 따라 관리업무를 인계하기 전의 사업주체 다. 주택관리업자 라. 임대사업자 마. 「 민간임대주택에 관한 특별법 」 제2조제11호에 
         따른 주택임대관리업자(시설물 유지ㆍ보수ㆍ개량 및 그 밖의 주택관리 업무를 수행하는 경우에 한정한다) 법제처 1 국가법령정보센터 공동주택관리법 
         11. “주택관리사보”란 제67조제1항에 따라 주택관리사보 합격증서를 발급받은 사람을 말한다. 12. “주택관리사”란 제67조제2항에 따라 주택관리사 
         자격증을 발급받은 사람을 말한다. 13. “주택관리사등”이란 주택관리사보와 주택관리사를 말한다. 14. “주택관리업”이란 공동주택을 안전하고 효율적으로
           관리하기 위하여 입주자등으로부터 의무관리대상 공동주택 의관리를 위탁받아 관리하는 업(業)을 말한다. 15. “주택관리업자”란 주택관리업을
             하는 자로서 제52조제1항에 따라 등록한 자를 말한다. 16. 삭제<2016. 1. 19.> 17. 삭제<2016. 1. 19.> 1. “장기수선계획”이란 공동주택을 
             오랫동안 안전하고 효율적으로 사용하기 위하여 필요한 주요 시설의 교체 및 보수 등에 관하여 제29조제1항에 따라 수립하는 장기계획을 말한다. 
             2. “임대주택”이란 「민간임대주택에 관한 특별법」에 따른 민간임대주택 및 「공공주택 특별법」에 따른 공공임대주택을말한다. 
             3. “임대사업자”란 「민간임대주택에 관한 특별법」 제2조제7호에 따른 임대사업자 및 「공공주택 특별법」 제4조제 1항에 따른 공공주택사업자를 말한다.
               4. “임차인대표회의”란 「민간임대주택에 관한 특별법」 제52조에 따른 임차인대표회의 및 「공공주택 특별법」 제 50조에 따라 준용되는 임차인대표회의를 
               말한다. ② 이 법에서 따로 정하지 아니한 용어의 뜻은 「주택법」에서 정한 바에 따른다. 제3조(국가 등의 의무)
                 ① 국가 및 지방자치단체는 공동주택의 관리에 관한 정책을 수립ㆍ시행할 때에는 다음 각 호의 사항을 위하여 노력하여야 한다.
                   1. 공동주택에 거주하는 입주자등이 쾌적하고 살기 좋은 주거생활을 할 수 있도록 할 것 2. 공동주택이 투명하고 체계적이며 평온하게
                     관리될 수 있도록 할 것 3. 공동주택의 관리와 관련한 산업이 건전한 발전을 꾀할 수 있도록 할 것 
                     ② 관리주체는 공동주택을 효율적이고 안전하게 관리하여야 한다.
"""

chunker = SemanticChunker("sentence-transformers/paraphrase-MiniLM-L6-v2", max_chunk_length=500, threshold=0.7)
chunks = chunker.split_text(text)

# 결과 출력
for idx, chunk in enumerate(chunks):
    print(f"Chunk {idx + 1}: {chunk}\n")
