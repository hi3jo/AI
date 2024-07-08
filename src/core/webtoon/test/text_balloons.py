from PIL import Image, ImageDraw, ImageFont

# Load the image
image_path = "webtoonStyle.png"
image = Image.open(image_path)

# Load the font
font_path = "ChosunCentennial_ttf.ttf"
font = ImageFont.truetype(font_path, 40)

# Coordinates for the text
coordinates = [(290, 40), (500, 330)]
new_text = "안녕 그리고 미안"

# Create a drawing context
draw = ImageDraw.Draw(image)

# Draw the text
for coord in coordinates:
    draw.rectangle((coord[0] - 10, coord[1] - 10, coord[0] + 100, coord[1] + 50), fill="white")
    draw.text(coord, new_text, font=font, fill="black")

# Save the modified image
modified_image_path = "webtoonStyle_modified.png"
#image.save(modified_image_path)
image.save("aa.png", "PNG")
modified_image_path