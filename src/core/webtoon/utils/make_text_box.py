from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

#FONT_PATH = r"C:\ai\adventurer\AI\src\core\webtoon\font\ChosunCentennial_ttf.ttf"
# 현재 파일의 디렉토리를 기준으로 폰트 파일 경로 설정
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_DIR, 'font', 'ChosunCentennial_ttf.ttf')

# 한국말 설명 추가.
def  make_korean_balloons(image_cut, speech):
   
    # 1. Load the image : 1컷씩 생성된 이미지를 받아옴 : 
    image = image_cut
    
    # 2. font 적용 : Load the font
    font_path = FONT_PATH
    font = ImageFont.truetype(font_path, 30)    # 원래 크기(40)의 50%
    
    # Coordinates for the text
    #coordinates = [(290, 40), (500, 330)]
    
    new_text = speech

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Calculate text size using textbbox
    text_bbox = draw.textbbox((0, 0), new_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate coordinates for the text to be centered at the bottom
    x = (image.width - text_width) / 2
    y = image.height - text_height - 20  # 하단에서 텍스트 높이만큼 위로 이동

    # Create a semi-transparent rectangle
    rectangle_image = Image.new('RGBA', (text_width + 20, text_height + 20), (255, 255, 255, 25))  # 10% 불투명도
    image.paste(rectangle_image, (int(x - 10), int(y - 10)), rectangle_image)

    # Draw the text
    draw.text((x, y), new_text, font=font, fill="black")

    # Draw the text
    # for coord in coordinates:
    #     draw.rectangle((coord[0] - 10, coord[1] - 10, coord[0] + 100, coord[1] + 50), fill="white")
    #     draw.text(coord, new_text, font=font, fill="black")

    # 현재 시간을 기반으로 파일 이름 생성
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_folder_path = os.path.join(BASE_DIR, 'img')
    
    # img 폴더가 존재하지 않으면 생성
    if not os.path.exists(img_folder_path):
        os.makedirs(img_folder_path)
    
    # 파일 경로 설정
    file_name = f"{current_time}.png"
    file_path = os.path.join(img_folder_path, file_name)
    
    # 이미지 저장
    image.save(file_path, "PNG")

    # 리턴 수정된 이미지 객체
    return image

