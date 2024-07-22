# 4 유틸리티 모듈
# 텍스트 길이 제한 및 메타데이터 포맷팅 함수 정의


import logging

logger = logging.getLogger(__name__)

# 텍스트 길이를 제한하는 함수
def truncate_text(text, max_tokens):
    tokens = text.split()
    if len(tokens) > max_tokens:
        return " ".join(tokens[:max_tokens])
    return text
# def truncate_text(text, max_tokens):
#     if isinstance(text, list):
#         text = ' '.join(text)
#     tokens = text.split()
#     if len(tokens) <= max_tokens:
#         return text
#     return ' '.join(tokens[:max_tokens])

# 메타데이터 포맷팅 함수
def format_metadata_response(metadata_list):
    response = ""
    for metadata in metadata_list:
        response += f"**법원명**: {metadata.get('법원명', '없음')}\n"
        response += f"**사건번호**: {metadata.get('사건번호', '없음')}\n"
        response += f"**판결요지**: {metadata.get('판결요지', '없음')}\n\n"
    logger.info("메타데이터 출력 중: 법원명, 사건번호, 판결요지")
    return response
