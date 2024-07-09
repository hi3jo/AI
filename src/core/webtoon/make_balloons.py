from PIL import Image, ImageDraw, ImageFont
import os

#FONT_PATH = r"C:\ai\adventurer\AI\src\core\webtoon\ChosunCentennial_ttf.ttf"
# 현재 파일의 디렉토리를 기준으로 폰트 파일 경로 설정
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, 'ChosunCentennial_ttf.ttf')

# 한국말 설명 추가.
def make_korean_balloons(img, ct):
   
    # Load the image
    image = img
    # Load the font
    font_path = FONT_PATH
    font = ImageFont.truetype(font_path, 40)
    # Coordinates for the text
    coordinates = [(290, 40), (500, 330)]
    new_text = ct

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Draw the text
    for coord in coordinates:
        draw.rectangle((coord[0] - 10, coord[1] - 10, coord[0] + 100, coord[1] + 50), fill="white")
        draw.text(coord, new_text, font=font, fill="black")

    image.save("gg.png", "PNG")

    # 리턴 수정된 이미지 객체
    return image

