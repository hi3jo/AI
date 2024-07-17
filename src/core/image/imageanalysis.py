import torch
import torchvision.transforms as transforms
from PIL import Image
from efficientnet_pytorch import EfficientNet
import io
import os
from fastapi import UploadFile

# 클래스 이름 딕셔너리
class_names = {0: 'couplewalking', 1: 'hug', 2: 'kiss', 3: 'normal'}

# EfficientNet 모델 로드
model_path = os.path.join(os.path.dirname(__file__), 'modelAdambatch32epoch30.pt')
model = EfficientNet.from_name('efficientnet-b0')
model._fc = torch.nn.Linear(model._fc.in_features, 4)  # 클래스 수를 4로 설정
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()

# 이미지 전처리 함수
def preprocess_image(image: Image.Image):
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = preprocess(image).unsqueeze(0)
    return image

# 이미지 분석 함수
def analyze_image(file: UploadFile):
    image = Image.open(io.BytesIO(file.file.read())).convert('RGB')
    input_tensor = preprocess_image(image)

    with torch.no_grad():
        output = model(input_tensor)
        _, predicted = torch.max(output, 1)
        prediction = predicted.item()

    predicted_class = class_names[prediction]
    is_possible = predicted_class in ['couplewalking', 'hug', 'kiss']

    return {
        'answer': f'{predicted_class}',
        'isPossible': is_possible
    }
