# Adobe "Connecting the Dots" Hackathon – Project README

## 📚 Project Overview
This repository contains three solutions for extracting structured information and insights from PDF documents:

- **outline_extractor:** PDF Structured Outline Extractor (font-based, logic + clustering)
- **persona_insight_extractor:** Persona-Driven Insight Extractor (semantic ranking, persona/job intent, summarization)
- **semantic_outline_extractor:** Semantic PDF Outline Extractor (SBERT + clustering)

All solutions are designed to run **fully offline** after initial setup.

---

## 🗂️ Folder Structure
```
AdobeHackathon/
├── outline_extractor/
│   ├── extractor.py
│   ├── utils.py
│   ├── requirements.txt
│   ├── input/           # Place your test PDFs here
│   └── output/          # Extracted JSON files will appear here
├── persona_insight_extractor/
│   ├── extractor_1b.py
│   ├── heading_utils.py
│   ├── semantic_utils.py
│   ├── requirements.txt
│   ├── input/           # Place your test PDFs and persona.json here
│   ├── output/          # Output JSON and logs
│   ├── pretrained_model/        # (Required) Local SBERT model
│   └── pretrained_summarizer/   # (Optional) Local summarization model
├── semantic_outline_extractor/
│   ├── main.py
│   ├── utils.py
│   ├── input/           # Place your test PDFs here
│   ├── output/          # Extracted JSON files will appear here
│   └── pretrained_model/        # (Required) Local SBERT model
└── README.md
```

---

## 🚫 Offline Setup Instructions

### 1. **Install Python Dependencies**
For each extractor, install dependencies from the respective `requirements.txt`:
```bash
pip install -r "outline_extractor/requirements.txt"
pip install -r "persona_insight_extractor/requirements.txt"
pip install -r "semantic_outline_extractor/requirements.txt"
```

### 2. **Prepare Local Models (One-Time, Requires Internet)**
#### **A. SBERT Model (for persona_insight_extractor and semantic_outline_extractor)**
On a machine with internet:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L12-v2')
model.save('pretrained_model')
```
Copy the `pretrained_model` folder to:
- `persona_insight_extractor/pretrained_model`
- `semantic_outline_extractor/pretrained_model`

#### **B. Summarization Model (Optional, for persona_insight_extractor)**
On a machine with internet:
```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
model_name = 'facebook/bart-large-cnn'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
model.save_pretrained('pretrained_summarizer')
tokenizer.save_pretrained('pretrained_summarizer')
```
Copy the `pretrained_summarizer` folder to:
- `persona_insight_extractor/pretrained_summarizer`

---

## 🏃 How to Run Each Solution

### **A. outline_extractor – PDF Structured Outline Extractor**
1. Place your PDF files in `outline_extractor/input/`.
2. Run:
   ```bash
   cd "outline_extractor"
   python extractor.py
   ```
3. Output JSON files will appear in `outline_extractor/output/`.

### **B. persona_insight_extractor – Persona-Driven Insight Extractor**
1. Place your PDF files in `persona_insight_extractor/input/`.
2. Add a `persona.json` file in `persona_insight_extractor/input/` with the following structure:
   ```json
   {
     "persona": "PhD Researcher in Computational Biology",
     "job_to_be_done": "Prepare a literature review focusing on methodologies, datasets, and performance benchmarks"
   }
   ```
3. Ensure `pretrained_model/` (SBERT) and optionally `pretrained_summarizer/` (summarization) folders are present.
4. Run:
   ```bash
   cd "persona_insight_extractor"
   python extractor_1b.py
   ```
5. Output and summaries will be printed in the terminal and saved to `persona_insight_extractor/output/challenge1b_output.json`.

### **C. semantic_outline_extractor – Semantic PDF Outline Extractor**
1. Place your PDF files in `semantic_outline_extractor/input/`.
2. Ensure `pretrained_model/` (SBERT) folder is present.
3. Run:
   ```bash
   cd "semantic_outline_extractor"
   python main.py
   ```
4. Output JSON files will appear in `semantic_outline_extractor/output/`.

---

## ❗ Troubleshooting
- If you see an error about a missing model, make sure the required `pretrained_model` or `pretrained_summarizer` folders are present in the correct directory.
- No internet connection is required after the initial model download and setup.
- All dependencies are installable via pip and do not require online access after installation.

---

## Multilingual PDF Analysis with spaCy

### Overview
This application now supports multilingual PDF analysis using spaCy's multilingual model (`xx_ent_wiki_sm`). You can extract language, named entities, key phrases, and perform text analysis on PDFs in 55+ languages directly from the GUI.

### Features
- **Language Detection:** Detects the primary language of the PDF text.
- **Named Entity Recognition:** Extracts named entities (people, organizations, locations, etc.) from the document.
- **Key Phrase Extraction:** Identifies important noun phrases and key terms.
- **Text Structure Analysis:** Provides statistics such as number of sentences, tokens, and entity types.

### Requirements
- Python 3.8+
- spaCy >=3.0
- spaCy multilingual model (`xx_ent_wiki_sm`)
- Compatible NumPy version (`numpy<2` recommended)

### How to Use
1. **Install Requirements:**
   - Run `pip install -r requirements.txt`
   - Run `python -m spacy download xx_ent_wiki_sm`
   - If you encounter errors with NumPy 2.x, downgrade with `pip install "numpy<2"`
2. **Start the API Server:**
   - `python api_server.py`
3. **Open the GUI:**
   - Load a PDF file.
   - Switch to the "Multilingual" mode using the mode buttons.
   - Use the "Analyze Text" or "Extract Entities" buttons to perform multilingual analysis.

### Troubleshooting
- If you see errors related to NumPy, ensure you are using `numpy<2`.
- Make sure the API server is running before using the GUI features.

### Example Output
- Language detected: English
- Named Entities: ["John Doe", "New York"]
- Key Phrases: ["machine learning", "natural language processing"]
- Entity Types: {"PERSON": 2, "GPE": 1}

---
# PDF-Intelliview
