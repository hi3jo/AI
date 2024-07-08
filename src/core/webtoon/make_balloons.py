from PIL import Image, ImageDraw, ImageFont

FONT_PATH = r"C:\ai\adventurer\AI\src\core\webtoon\ChosunCentennial_ttf.ttf"
def make_korean_balloons(img):
    
    # Load the image
    print("4...make_korean_balloons 펑션")
    image = img
    print("4.1....make_korean_balloons 펑션")
    # Load the font
    font_path = FONT_PATH
    print("4.2....make_korean_balloons 펑션")
    font = ImageFont.truetype(font_path, 40)
    print("4.3....make_korean_balloons 펑션")
    # Coordinates for the text
    coordinates = [(290, 40), (500, 330)]
    new_text = "안녕 그리고 미안"

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Draw the text
    for coord in coordinates:
        draw.rectangle((coord[0] - 10, coord[1] - 10, coord[0] + 100, coord[1] + 50), fill="white")
        draw.text(coord, new_text, font=font, fill="black")

    image.save("gg.png", "PNG")

    # 리턴 수정된 이미지 객체
    return image

