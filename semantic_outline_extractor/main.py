# main.py

from .utils import extract_outline
from pathlib import Path
import json
import time

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_semantic_outline_from_file(pdf_path):
    try:
        from .utils import extract_outline
    except ImportError as e:
        return {"error": f"Failed to import utils: {e}"}
    
    try:
        title, outline = extract_outline(pdf_path)
        return {"title": title, "outline": outline}
    except Exception as e:
        return {"error": f"Failed to extract semantic outline: {str(e)}"}

for pdf_path in INPUT_DIR.glob("*.pdf"):
    print(f"\n📄 Processing: {pdf_path.name}")
    start = time.time()
    try:
        title, outline = extract_outline(str(pdf_path))
        with open(OUTPUT_DIR / f"{pdf_path.stem}.json", "w", encoding="utf-8") as f:
            json.dump({"title": title, "outline": outline}, f, indent=2)
        print(f"✅ Done: {pdf_path.name} | Title: {title} | Headings: {len(outline)} | Time: {time.time() - start:.2f}s")
    except Exception as e:
        print(f"❌ Error in {pdf_path.name}: {e}")
