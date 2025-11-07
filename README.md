# AI Engine - PDF Full Analysis (Demo)

This project is a demonstration pipeline that converts a multi-page technical PDF into images, classifies pages, analyzes floorplans, reconstructs a simple 3D wall model (OBJ), and produces combined material estimates.

## How to run

1. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Run pipeline on a PDF:
```bash
python main.py path/to/technical_drawings.pdf output_folder
```

Output will be in `output_folder` including `result_full.json` and per-page `model.obj` files.
