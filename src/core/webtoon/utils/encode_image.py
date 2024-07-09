from io import BytesIO
import base64

def b64encode(combined_img):
    buffered = BytesIO()
    combined_img.save(buffered, format="PNG")
    encode_img = base64.b64encode(buffered.getvalue()).decode()
    return encode_img