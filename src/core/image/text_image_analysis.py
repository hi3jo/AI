from typing import List
from fastapi import UploadFile
from src.core.image.nlp_analysis import analyze_text_from_image

async def analyze_text_from_images(files: List[UploadFile]):
    nlp_result = await analyze_text_from_image(files)
    
    combined_analysis = ""
    is_possible = False

    for result in nlp_result["results"]:
        analysis = result["analysis"]
        
        # 중복된 내용 제거
        analysis_parts = analysis.split("\n\n")
        analysis = " ".join(analysis_parts)  # 모든 부분을 공백으로 연결
        combined_analysis += analysis + " "
        
        # 성적인 내용 및 부적절한 관계 가능성 확인
        has_sexual_content = any(phrase in analysis.lower() for phrase in [
            "성적인 내용이 포함",
            "성적인 내용이 있",
            "성적인 암시가 있",
            "성적인 표현이 있"
        ]) and "성적인 내용이 없" not in analysis.lower()

        is_inappropriate_relationship = any(phrase in analysis.lower() for phrase in [
            "부적절한 관계로 보",
            "부적절한 관계의 가능성",
            "부적절한 관계를 암시"
        ]) and "부적절한 관계로 보이지 않" not in analysis.lower()

        is_possible = is_possible or has_sexual_content or is_inappropriate_relationship
    
    # 통합된 분석 결과에서 중복 제거 및 요약
    combined_analysis_parts = combined_analysis.split("\n\n")
    unique_parts = []
    for part in combined_analysis_parts:
        if part not in unique_parts:
            unique_parts.append(part)
    combined_analysis = "\n\n".join(unique_parts)
    
    # 응답 형식 수정
    result = {
        "answer": combined_analysis.strip(),
        "isPossible": is_possible
    }
    
    return result