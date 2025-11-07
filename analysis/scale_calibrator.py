import cv2, math
from detectors.text_ocr import extract_numbers_from_text, ocr_image_to_text
from typing import Optional, List, Tuple
import numpy as np

def find_candidate_dimensions(img) -> List[float]:
    text = ocr_image_to_text(img)
    nums = extract_numbers_from_text(text)
    # filter likely meter values (>=0.2 and <=100)
    return [n for n in nums if n>0.1 and n<1000]

def manual_calibrate(known_length_m: float, p1: Tuple[int,int], p2: Tuple[int,int]) -> float:
    px_len = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
    if px_len <= 0:
        raise ValueError("Pixel length zero")
    return known_length_m / px_len

# helper: compute pixel distance between two points
def pixel_distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])
