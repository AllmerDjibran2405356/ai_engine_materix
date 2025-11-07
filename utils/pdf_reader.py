import fitz
from pathlib import Path
from typing import List

def pdf_to_images(pdf_path: str, out_folder: str, dpi: int = 300) -> List[str]:
    out = Path(out_folder)
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    images = []
    for i, page in enumerate(doc):
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        p = out / f"page_{i+1:03}.jpg"
        pix.save(str(p))
        images.append(str(p))
    return images
