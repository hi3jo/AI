from PIL import Image as PILImage, ImageDraw, ImageFont

# 이미지 열기
image_path = "webtoonStyle.png"
img = PILImage.open(image_path)

# 말풍선에 있는 기존 텍스트 지우기 (흰색으로 덮기)
draw = ImageDraw.Draw(img)

# 한글 폰트 설정 (업로드된 폰트 파일 경로)
font_path = "ArialTh.ttf"
font = ImageFont.truetype(font_path, 24)

# 말풍선 위치 및 크기 설정 (예시 좌표와 크기, 필요시 조정)
bubble1_position = (220, 30, 320, 80)    # (left, top, right, bottom)
bubble2_position = (430, 250, 530, 300)  # (left, top, right, bottom)

# 말풍선 덮기
draw.rectangle(bubble1_position, fill="white")
draw.rectangle(bubble2_position, fill="white")

# 새로운 텍스트 추가
text = "타지로 이사와서 의지할 사람이 당신밖에 없었잖아."
text_position1 = (bubble1_position[0] + 10, bubble1_position[1] + 10)
text_position2 = (bubble2_position[0] + 10, bubble2_position[1] + 10)

draw.text(text_position1, text, font=font, fill="black")
draw.text(text_position2, text, font=font, fill="black")

# 결과 이미지 저장
output_path = "webtoonStyle_with_text.png"
img.save(output_path)

output_path