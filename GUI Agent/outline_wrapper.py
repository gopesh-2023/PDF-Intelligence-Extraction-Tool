import sys
import os
import json
import fitz  
from outline_extractor.utils import extract_headings

def main():
    if len(sys.argv) < 2:
        print("[ERROR] No PDF file path provided.")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"[ERROR] File not found: {pdf_path}")
        sys.exit(1)

    try:
        doc = fitz.open(pdf_path)
        title, outline = extract_headings(doc)

        result = {
            "file": os.path.basename(pdf_path),
            "title": title,
            "outline": outline
        }

        output_dir = os.path.join('outline_extractor', 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}.json")

        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        print("Outline Extraction Results:\n")
        print(f"File: {result['file']}")
        print(f"Title: {result['title']}")
        print(f"Headings: {len(result['outline'])}")
        for item in result['outline'][:5]:
            print(f"  - {item['text']} (Page {item['page']})")

        print(f"\nSaved to: {output_file}")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
