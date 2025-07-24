# backend/ocr_utils.py
import pytesseract
import cv2
import numpy as np
from PIL import Image

def preprocess_image(file_path):
    img = cv2.imread(file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

def extract_marks(file_path):
    preprocessed = preprocess_image(file_path)
    temp_file = 'temp_processed.png'
    cv2.imwrite(temp_file, preprocessed)

    text = pytesseract.image_to_string(Image.open(temp_file))
    # Dummy structured extraction logic (modify as per your marksheet layout)
    result = {
        "RRN": "123456",
        "Name": "Vipranan",
        "Part-A": "40",
        "Part-B": "35",
        "Total": "75"
    }
    return result
