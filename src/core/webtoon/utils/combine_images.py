from PIL import Image as PILImage
from datetime import datetime

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

def combine_images_fix_size(images):
    
    # 이미지를 2x2 그리드로 합치기
    grid_size = 1024
    combined_img = PILImage.new('RGB', (grid_size * 2, grid_size * 2))

    combined_img.paste(images[0], (0, 0))
    combined_img.paste(images[1], (grid_size, 0))
    combined_img.paste(images[2], (0, grid_size))
    combined_img.paste(images[3], (grid_size, grid_size))
    return combined_img