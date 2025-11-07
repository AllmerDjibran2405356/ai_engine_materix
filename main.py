import sys
from pipe.run_full_pdf_pipeline import run

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input.pdf> [output_folder]")
        return

    pdf_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output"

    run(pdf_path, out_dir)

if __name__ == "__main__":
    main()
