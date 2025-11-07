from pdf2image import convert_from_path
from pathlib import Path

def pdf_to_images(pdf_path, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    pages = convert_from_path(pdf_path)
    paths = []

    for i, page in enumerate(pages, start=1):
        img_path = out_dir / f"page_{i:03d}.jpg"
        page.save(img_path, "JPEG")
        paths.append(str(img_path))

    return paths
