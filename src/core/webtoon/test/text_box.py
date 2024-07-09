from PIL import Image, ImageDraw, ImageFont

#텍스트 길이에 맞게 하단에 박스 생성하게 함.

# Load the image
image_path = "webtoonStyle.png"
image = Image.open(image_path)

# Load the font and resize it to 50%
font_path = "ChosunCentennial_ttf.ttf"
font = ImageFont.truetype(font_path, 20)  # 원래 크기의 50%

# Text to be added
new_text = "안녕 그리고 미안"

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

# Save the modified image
modified_image_path = "tttttt.png"
image.save(modified_image_path, "PNG")