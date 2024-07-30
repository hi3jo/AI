from typing import List
from fastapi import UploadFile
from src.core.image.nlp_analysis import analyze_text_from_image

async def analyze_text_from_images(files: List[UploadFile]):
    nlp_result = await analyze_text_from_image(files)
    
    results = []

    for result in nlp_result["results"]:
        analysis = result["analysis"]
        filename = result["filename"]

        print(f"Raw API response for {filename}: {analysis}")

        # 결과 구성
        sexual_content = "성적인 내용이 포함되어 있습니다." if analysis.get("성적표현", False) else "성적인 내용이 없습니다."
        inappropriate_relationship = "부적절한 관계의 가능성이 있습니다." if analysis.get("부적절관계", False) else "부적절한 관계로 보여지기 어렵습니다."

        final_result = {
            "filename": filename,
            "answer": {
                "대화내용": analysis.get("대화내용", ""),
                "성적표현": sexual_content,
                "부적절관계": inappropriate_relationship
            },
            "isPossible": analysis.get("성적표현", False) or analysis.get("부적절관계", False)
        }
        
        results.append(final_result)
    
    return {"results": results}