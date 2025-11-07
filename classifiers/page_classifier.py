from detectors.text_ocr import ocr_image_to_text
import cv2

def classify_page(img, th) -> str:
    text = ocr_image_to_text(img).lower()
    if any(k in text for k in ['denah','floor plan','floorplan','rencana']):
        return 'floorplan'
    if any(k in text for k in ['tampak','elevation','facade']):
        return 'elevation'
    if any(k in text for k in ['potongan','section']):
        return 'section'
    # fallback using contours heuristic
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large = [c for c in cnts if cv2.contourArea(c) > 1000]
    return 'floorplan' if len(large) >= 1 else 'unknown'
