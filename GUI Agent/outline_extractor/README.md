# 📘 Adobe “Connecting the Dots” Hackathon – outline_extractor
## 🔎 PDF Structured Outline Extractor

### 🎯 Objective
This solution extracts a clean hierarchical outline from any PDF, including:
- Document **Title**
- Heading levels: **H1**, **H2**, and **H3**
- **Page numbers** for each heading

The output is returned as a JSON in the format:
```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
🧠 Approach
This extractor combines font-based heuristics with KMeans clustering to reliably infer heading levels across diverse PDF styles:

📌 Techniques Used:
PyMuPDF for parsing font size, font name, text, and position

KMeans clustering to dynamically group font sizes within each document

Heading detection based on:

Font size clusters

Position on page

Text appearance patterns (e.g., title casing)

Title is extracted from the first detected H1 (largest font cluster)

This makes it adaptive to each PDF’s unique styling — without relying on hardcoded font rules.

🚀 Running Instructions
📁 Folder Structure
graphql
Copy
Edit
adobe/
├── Dockerfile
├── extractor.py
├── utils.py
├── requirements.txt
├── README.md
├── input/          # Place your test PDFs here
└── output/         # Extracted JSON files will appear here
🐳 Docker Build
Make sure Docker is installed and running. Then:

Navigate to this folder in terminal:

bash
Copy
Edit
cd path/to/adobe
Build the Docker image:

bash
Copy
Edit
docker build --platform linux/amd64 -t heading_extractor .
🧪 Run the Extractor
bash
Copy
Edit
docker run --rm -v %cd%/input:/app/input -v %cd%/output:/app/output --network none heading_extractor
📝 This will:

Read all PDFs from /input

Extract title and headings

Output one .json per .pdf to /output

✅ Constraints Satisfied
Constraint	Status
Model Size	No model used (pure logic-based) ✅
Execution Time	<10 seconds on 50-page PDF ✅
Internet Access	Not required ✅
Platform	Compatible with linux/amd64 ✅
CPU-Only	Yes ✅

📚 Libraries Used
PyMuPDF – PDF parsing

scikit-learn – KMeans clustering

❗ What Not to Do – Avoided
❌ No font-size hardcoding

❌ No internet access or API calls

❌ No file-specific hacks

❌ No GPU dependencies

