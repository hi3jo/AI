from PIL import Image as PILImage
from datetime import datetime
import requests
from io import BytesIO

# 현재 적용하고 있는 코드
def combine_images_fix_size(images):
    
    # 이미지를 2x2 그리드로 합치기
    grid_size = 1024
    combined_img = PILImage.new('RGB', (grid_size * 2, grid_size * 2))

    combined_img.paste(images[0], (0, 0))
    combined_img.paste(images[1], (grid_size, 0))
    combined_img.paste(images[2], (0, grid_size))
    combined_img.paste(images[3], (grid_size, grid_size))
    return combined_img



# 사이즈 조정하는 로직이 포함된 코드이나 원하는 결과물은 나오지 않음.
def combine_images(images, rows, cols, scale):
    
    print("combine_images : 이미지 크기 줄여주는지 확인할 것.")
    img_width, img_height = images[0].width, images[0].height
    new_width, new_height = int(img_width * scale), int(img_height * scale)

    # 새로운 크기로 이미지 크기 조정
    resized_images = [img.resize((new_width, new_height), PILImage.Resampling.LANCZOS) for img in images]

    grid_width = cols * new_width
    grid_height = rows * new_height
    combined_img = PILImage.new('RGB', (grid_width, grid_height))

    for idx, img in enumerate(resized_images):
        x_offset = (idx % cols) * new_width
        y_offset = (idx // cols) * new_height
        combined_img.paste(img, (x_offset, y_offset))
    
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{current_time}.png"  # 파일명 생성
    combined_img.save(file_name, "PNG")  # 현재 경로에 저장
    print(f"이미지가 {file_name}에 저장되었습니다.")
    return combined_img



#image_url = response['data'][0]['url']
#print(f"Generated image for panel {i+1}: {image_url}")
#generated_images.append(image_url)
#generated_images = []  # Dalle3로부터 생성된 이미지를 담을 리스트
def combine(generated_images):
 # 모든 이미지를 다운로드 및 합치기
    images = []
    for image_url in generated_images:
        response = requests.get(image_url)
        img = PILImage.open(BytesIO(response.content))
        images.append(img)

    # 4개의 이미지를 하나로 합침
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = PILImage.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.width
    
    return new_im
