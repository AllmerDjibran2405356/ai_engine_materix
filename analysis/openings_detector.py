import cv2, numpy as np
from typing import List, Tuple

def detect_openings_template(img, templates: List[np.ndarray], threshold=0.72):
    gray = img if len(img.shape)==2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    boxes = []
    for tpl in templates:
        res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
        ys, xs = np.where(res >= threshold)
        h, w = tpl.shape
        for (y,x) in zip(ys,xs):
            boxes.append((x,y,w,h,res[y,x]))
    return boxes

def detect_openings_by_gap(segs, gap_px=30):
    # Naive: return empty list (template is stronger approach)
    return []
