from PIL import Image
import pytesseract
import base64
from io import BytesIO

def extract_text_from_image(b64_image):
    image = Image.open(BytesIO(base64.b64decode(b64_image)))
    return pytesseract.image_to_string(image)
