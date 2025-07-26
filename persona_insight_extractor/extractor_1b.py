import os, json, datetime
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from heading_utils import extract_headings_and_text
from semantic_utils import rank_sections_by_similarity

INPUT_DIR = "input"
OUTPUT_DIR = "output"

os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    summarizer_model_path = os.path.join(os.path.dirname(__file__), 'pretrained_summarizer')
    if not os.path.exists(summarizer_model_path):
        print(f"[ERROR] Local summarization model not found at {summarizer_model_path}. Please download and place it here before running offline.")
        summarizer = None
    else:
        summarizer = pipeline("summarization", model=summarizer_model_path, tokenizer=summarizer_model_path)
    def summarize_text(text):
        if summarizer is None or len(text) < 50:
            return text[:300] + ("..." if len(text) > 300 else "")
        try:
            summary = summarizer(text[:1024], max_length=60, min_length=20, do_sample=False)[0]['summary_text']
            return summary
        except Exception as e:
            print(f"[WARNING] Summarization failed: {e}. Using snippet.")
            return text[:300] + ("..." if len(text) > 300 else "")
except ImportError:
    summarizer = None
    def summarize_text(text):
        print("[WARNING] transformers not installed, using longer snippet instead of summary.")
        return text[:300] + ("..." if len(text) > 300 else "")

def load_persona_job():
    persona_path = os.path.join(INPUT_DIR, "persona.json")
    if not os.path.exists(persona_path):
        print(f"[ERROR] persona.json not found in '{INPUT_DIR}'. Please provide it.")
        sys.exit(1)
    with open(persona_path, "r") as f:
        data = json.load(f)
    return data["persona"], data["job_to_be_done"]

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"[ERROR] Input folder '{INPUT_DIR}' does not exist.")
        sys.exit(1)
    if not os.path.exists(OUTPUT_DIR):
        print(f"[INFO] Output folder '{OUTPUT_DIR}' does not exist. Creating it.")
        os.makedirs(OUTPUT_DIR)
    persona, job = load_persona_job()
    combined_query = f"{persona}. Task: {job}"

    pdfs = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    if not pdfs:
        print(f"[WARNING] No PDF files found in '{INPUT_DIR}'.")
        return
    all_sections = []
    for filename in pdfs:
        doc_path = os.path.join(INPUT_DIR, filename)
        try:
            doc_sections = extract_headings_and_text(doc_path, filename)
            all_sections.extend(doc_sections)
        except Exception as e:
            print(f"[ERROR] Failed to process {filename}: {e}")
    if not all_sections:
        print("[WARNING] No sections extracted from any PDF.")
        return
    try:
        ranked = rank_sections_by_similarity(all_sections, combined_query)
    except Exception as e:
        print(f"[ERROR] Failed to rank sections by similarity: {e}")
        return
    output = {
        "metadata": {
            "documents": pdfs,
            "persona": persona,
            "job_to_be_done": job,
            "timestamp": datetime.datetime.now().isoformat()
        },
        "sections": [],
        "subsection_analysis": []
    }
    for i, item in enumerate(ranked[:10]):
        output["sections"].append({
            "document": item["document"],
            "page": item["page"],
            "section_title": item["title"],
            "importance_rank": i+1
        })
        output["subsection_analysis"].append({
            "document": item["document"],
            "page": item["page"],
            "refined_text": item["text"],
            "importance_rank": i+1
        })
    # Group ranked sections by document
    persona_outline = {}
    for item in ranked:
        doc = item['document']
        if doc not in persona_outline:
            persona_outline[doc] = []
        if len(persona_outline[doc]) < 5:
            persona_outline[doc].append({
                'page': item['page'],
                'title': item['title'],
                'text': item['text']
            })
    # Print persona-based outline
    print("\n==============================")
    print("Persona-Driven Insight Extractor")
    print("==============================")
    print(f"Persona: {persona}")
    print(f"Job to be done: {job}\n")
    print("--- Top 10 Ranked Sections (Personalized) ---")
    for i, item in enumerate(ranked[:10]):
        summary = summarize_text(item['text'])
        print(f"{i+1}. [{item['document']}] Page {item['page']} - {item['title']}")
        print(f"   Summary: {summary}\n")
    print("--- Sub-section Analysis (Summaries) ---")
    for i, item in enumerate(ranked[:10]):
        summary = summarize_text(item['text'])
        print(f"{i+1}. [{item['document']}] Page {item['page']} - {item['title']}")
        print(f"   Sub-section summary: {summary}\n")
    print("--- Persona-based Outline (Top 5 per Document) ---")
    for doc, sections in persona_outline.items():
        print(f"\nDocument: {doc}")
        for i, sec in enumerate(sections, 1):
            print(f"  {i}. Page {sec['page']} - {sec['title']}")
            print(f"     Text: {sec['text'][:120]}{'...' if len(sec['text']) > 120 else ''}")
    print("\n[INFO] Full results saved to output/challenge1b_output.json\n")
    with open(os.path.join(OUTPUT_DIR, "challenge1b_output.json"), "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    try:
        import fitz
    except ImportError:
        print("[ERROR] PyMuPDF (fitz) is not installed. Please install it with 'pip install pymupdf'.")
        sys.exit(1)
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("[ERROR] sentence-transformers is not installed. Please install it with 'pip install sentence-transformers'.")
        sys.exit(1)
    main()
