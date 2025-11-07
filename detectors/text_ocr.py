import pytesseract, cv2
from typing import List
import re

def ocr_image_to_text(img) -> str:
    gray = img if len(img.shape)==2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    config = '--psm 6'
    text = pytesseract.image_to_string(th, config=config)
    return text

def extract_numbers_from_text(text: str) -> List[float]:
    nums = re.findall(r"\d+[.,]?\d*", text)
    def tofloat(s): return float(s.replace(',','.'))
    return [tofloat(n) for n in nums]
