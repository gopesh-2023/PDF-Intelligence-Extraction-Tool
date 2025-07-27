# main.py
import os
import fitz  # PyMuPDF
import json
try:
    from .utils import extract_headings
except ImportError:
    from utils import extract_headings
import sys

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def process_pdfs():
    if not os.path.exists(INPUT_DIR):
        print(f"[ERROR] Input folder '{INPUT_DIR}' does not exist.")
        sys.exit(1)
    if not os.path.exists(OUTPUT_DIR):
        print(f"[INFO] Output folder '{OUTPUT_DIR}' does not exist. Creating it.")
        os.makedirs(OUTPUT_DIR)
    pdfs = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    if not pdfs:
        print(f"[WARNING] No PDF files found in '{INPUT_DIR}'.")
        return
    for filename in pdfs:
        pdf_path = os.path.join(INPUT_DIR, filename)
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"[ERROR] Failed to open {filename}: {e}")
            continue
        try:
            title, outline = extract_headings(doc)
            output_json = {
                "title": title,
                "outline": outline
            }
            output_filename = filename.replace(".pdf", ".json")
            with open(os.path.join(OUTPUT_DIR, output_filename), "w") as f:
                json.dump(output_json, f, indent=2)
            print(f"[SUCCESS] Processed {filename} -> {output_filename}")
            print(f"  Title: {title}")
            print("  Outline:")
            for item in outline:
                print(f"    - {item['level']}: {item['text']} (Page {item['page']})")
        except Exception as e:
            print(f"[ERROR] Failed to process {filename}: {e}")

def extract_outline_from_file(pdf_path):
    import fitz
    try:
        doc = fitz.open(pdf_path)
        title, outline = extract_headings(doc)
        return {"title": title, "outline": outline}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    try:
        import fitz
    except ImportError:
        print("[ERROR] PyMuPDF (fitz) is not installed. Please install it with 'pip install pymupdf'.")
        sys.exit(1)
    process_pdfs()
