# import os
# import re
# import cv2
# import numpy as np
# from typing import List
# from paddleocr import PaddleOCR
# from fastapi import UploadFile
# import logging
# import tempfile

# # 로깅 설정
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # PaddleOCR 모델 초기화
# ocr_model = PaddleOCR(use_angle_cls=True, lang='korean')

# # 데이터 폴더 설정
# data_folder = "data"
# if not os.path.exists(data_folder):
#     os.makedirs(data_folder)

# def preprocess_text(text: str) -> str:
#     """
#     주어진 텍스트를 전처리하는 함수.
#     - 불필요한 공백 제거
#     - 특수 문자 제거
#     """
#     text = ' '.join(text.split())
#     text = re.sub(r'\s+', ' ', text)
#     text = re.sub(r'[^\w\s]', '', text)
#     logger.info(f"Preprocessed text: {text.strip()}")
#     return text.strip()

# def preprocess_image_with_color_mask(image, text_box_colors, background_colors):
#     """
#     배경색과 텍스트 박스를 구분하여 이미지를 전처리하는 함수.
#     """
#     try:
#         hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#         text_box_mask = np.zeros(hsv_image.shape[:2], dtype=np.uint8)

#         for color in text_box_colors:
#             lower_color = np.array(color['lower'], dtype=np.uint8)
#             upper_color = np.array(color['upper'], dtype=np.uint8)
#             mask = cv2.inRange(hsv_image, lower_color, upper_color)
#             text_box_mask = cv2.bitwise_or(text_box_mask, mask)

#         background_mask = np.zeros(hsv_image.shape[:2], dtype=np.uint8)
#         for color in background_colors:
#             lower_color = np.array(color['lower'], dtype=np.uint8)
#             upper_color = np.array(color['upper'], dtype=np.uint8)
#             mask = cv2.inRange(hsv_image, lower_color, upper_color)
#             background_mask = cv2.bitwise_or(background_mask, mask)

#         combined_mask = cv2.bitwise_and(text_box_mask, cv2.bitwise_not(background_mask))
#         text_boxes = cv2.bitwise_and(image, image, mask=combined_mask)
#         gray = cv2.cvtColor(text_boxes, cv2.COLOR_BGR2GRAY)
#         _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

#         logger.info("Image preprocessing complete")
#         return binary
#     except Exception as e:
#         logger.error(f"Error in preprocess_image_with_color_mask: {e}")
#         raise

# def remove_hand_region(image):
#     """
#     손가락 영역을 감지하여 제거하는 함수.
#     """
#     try:
#         lower_skin = np.array([0, 20, 70], dtype=np.uint8)
#         upper_skin = np.array([20, 255, 255], dtype=np.uint8)
#         hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#         mask = cv2.inRange(hsv, lower_skin, upper_skin)
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         for contour in contours:
#             area = cv2.contourArea(contour)
#             if area > 1000:
#                 cv2.drawContours(image, [contour], -1, (0, 0, 0), -1)

#         logger.info("Hand region removal complete")
#         return image
#     except Exception as e:
#         logger.error(f"Error in remove_hand_region: {e}")
#         raise

# def extract_text_regions(image):
#     """
#     이미지에서 텍스트 영역을 추출하는 함수.
#     """
#     try:
#         contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#         logger.info(f"Found {len(contours)} text regions")
#         return contours
#     except Exception as e:
#         logger.error(f"Error in extract_text_regions: {e}")
#         raise

# def is_relevant_text(text):
#     """
#     분석 대상 텍스트를 판별하는 함수 (가상의 로직, 필요시 수정).
#     """
#     return len(text) > 1

# def is_excluded_text(text):
#     """
#     제외 대상 텍스트를 판별하는 함수 (가상의 로직, 필요시 수정).
#     """
#     excluded_keywords = ["복사", "삭제", "전달", "나에게", "공지"]
#     return any(keyword in text for keyword in excluded_keywords)

# def extract_relevant_text(image_path):
#     """
#     이미지를 전처리하여 분석이 필요한 텍스트를 추출하는 함수.
#     """
#     try:
#         text_box_colors = [
#             {'lower': [0, 0, 200], 'upper': [180, 20, 255]},
#             {'lower': [25, 150, 150], 'upper': [35, 255, 255]},
#             {'lower': [0, 0, 0], 'upper': [180, 255, 50]},
#             {'lower': [0, 0, 200], 'upper': [180, 20, 255]},
#             {'lower': [35, 50, 50], 'upper': [85, 255, 255]}
#         ]

#         background_colors = [
#             {'lower': [0, 0, 200], 'upper': [180, 20, 255]},
#             {'lower': [0, 0, 0], 'upper': [180, 255, 50]},
#             {'lower': [90, 50, 70], 'upper': [128, 255, 255]}
#         ]

#         image = cv2.imread(image_path)
#         if image is None:
#             raise ValueError(f"Image not loaded properly from path: {image_path}")
        
#         logger.info("Image successfully loaded.")

#         image_without_hands = remove_hand_region(image)
#         binary_image = preprocess_image_with_color_mask(image_without_hands, text_box_colors, background_colors)
#         contours = extract_text_regions(binary_image)

#         relevant_text = []
#         for contour in contours:
#             x, y, w, h = cv2.boundingRect(contour)
#             cropped_image = image[y:y+h, x:x+w]
#             result = ocr_model.ocr(cropped_image, cls=True)
#             if result is None:
#                 logger.info("OCR model returned None for the cropped image.")
#                 continue

#             text = ""
#             if not result:
#                 logger.info("OCR model returned empty result for the cropped image.")
#                 continue

#             for line in result:
#                 if not line:
#                     logger.info("OCR model returned an empty line.")
#                     continue
                
#                 for word_info in line:
#                     if not word_info:
#                         logger.info("OCR model returned an empty word_info.")
#                         continue
                    
#                     text += word_info[1][0] + " "

#             if is_relevant_text(text) and not is_excluded_text(text):
#                 relevant_text.append(text.strip())

#         logger.info(f"Relevant text: {relevant_text}")
#         return "\n".join(relevant_text) if relevant_text else "No relevant text found"
#     except Exception as e:
#         logger.error(f"Error in extract_relevant_text: {e}")
#         raise

# async def perform_ocr(files: List[UploadFile]) -> dict:
#     try:
#         ocr_results = []
#         for file in files:
#             # 임시 파일 생성
#             with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
#                 contents = await file.read()
#                 temp_file.write(contents)
#                 temp_file_path = temp_file.name

#             # 임시 파일 경로를 사용하여 OCR 수행
#             text = extract_relevant_text(temp_file_path)
#             processed_text = preprocess_text(text)
#             ocr_results.append({"filename": file.filename, "text": processed_text})

#             # 임시 파일 삭제
#             os.unlink(temp_file_path)

#         logger.info(f"OCR results: {ocr_results}")
#         return {"results": ocr_results}

#     except Exception as e:
#         logger.error(f"Error in perform_ocr: {e}")
#         return {"error": str(e)}
