from pathlib import Path

from converters.pdf_to_image import pdf_to_images
from converters.image_processor import load_image

from analysis.wall_detector import detect_walls
from analysis.dimension_reader import extract_dimensions

from vectorization.vectorizer import vectorize_walls

from reconstruction.builder_3d import build_3d_scene
from reconstruction.export_glb import export_scene


def run(pdf_path, output_dir):

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    pages_dir = output_dir / "pdf_pages"
    pages_dir.mkdir(exist_ok=True)

    print("[INFO] Converting PDF to images...")
    images = pdf_to_images(pdf_path, pages_dir)
    print(f"[INFO] {len(images)} pages extracted")

    all_polygons = []
    all_dimensions = []

    # Process each page
    for i, img_path in enumerate(images, start=1):
        print(f"[INFO] Processing page {i}")

        img = load_image(img_path)

        walls = detect_walls(img)
        dims = extract_dimensions(img)
        polygons = vectorize_walls(walls, dims)

        print(f"[INFO] - Walls: {len(walls)}")
        print(f"[INFO] - Dimensions: {len(dims)}")
        print(f"[INFO] - Polygons: {len(polygons)}")

        all_polygons.extend(polygons)
        all_dimensions.extend(dims)

    print("[INFO] Building 3D model...")
    scene = build_3d_scene(all_polygons, all_dimensions)

    model_dir = output_dir / "model3d"
    model_dir.mkdir(exist_ok=True)

    model_path = model_dir / "model.glb"
    export_scene(scene, str(model_path))

    print(f"[SUCCESS] Model saved → {model_path}")
