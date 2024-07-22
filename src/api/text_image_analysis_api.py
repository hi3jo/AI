from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from src.core.image.nlp_analysis import classify_text
from src.core.image.pro_ocr import perform_ocr
from typing import List

def split_text(text: str, max_tokens: int = 1500) -> List[str]:
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word)
        if current_length + word_length + 1 > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length + 1
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

router = APIRouter()

@router.post("/analysis-text/")
async def upload_text_image(file: UploadFile = File(...), lang: str = 'kor'):
    try:
        ocr_results = await perform_ocr([file])
        
        # 모든 텍스트를 하나로 통합
        combined_text = ' '.join(result["text"] for result in ocr_results["results"])

        # 텍스트를 최대 토큰 수를 초과하지 않도록 나눔
        text_chunks = split_text(combined_text)

        # 각 청크에 대해 분석 및 요약 수행
        nlp_results = []

        for chunk in text_chunks:
            nlp_result = classify_text(chunk)
            nlp_results.append(nlp_result)

        # 개별 이미지 처리
        individual_results = []
        for result in ocr_results["results"]:
            try:
                nlp_result = classify_text(result["text"])
                individual_results.append({
                    "filename": result["filename"],
                    "ocr_result": result["text"],
                    "nlp_result": nlp_result
                })
            except ValueError as e:
                individual_results.append({"filename": result["filename"], "error": str(e)})

        # 기존 응답에 "answer"와 "isPossible" 필드 추가
        response = {
            "ocr": ocr_results, 
            "nlp": nlp_results,
            "individual_analysis": individual_results,
            "answer": nlp_results[0]["summary"] if nlp_results else "",  # 첫 번째 NLP 결과의 요약을 answer로 사용
            "isPossible": True  # 항상 True로 설정하거나, 필요에 따라 조건을 추가할 수 있습니다
        }

        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# text_image_analysis_router 정의
text_image_analysis_router = router
