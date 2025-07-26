# Adobe PDF Extractor - Offline GUI Application

## 🖥️ Overview

This is a comprehensive offline GUI application that integrates all three PDF extraction solutions from the Adobe "Connecting the Dots" Hackathon project:

1. **Outline Extractor** - Font-based structured outline extraction
2. **Persona Insights** - Persona-driven insight extraction with semantic ranking
3. **Semantic Outline** - AI-powered semantic outline extraction

## 🚀 Features

- **Fully Offline** - Works without internet connection after initial setup
- **Modern GUI** - Clean, tabbed interface with intuitive controls
- **Three Extraction Methods** - Choose the best approach for your needs
- **Real-time Progress** - Status updates and progress indicators
- **Batch Processing** - Process multiple PDFs at once
- **Results Preview** - View extraction results directly in the GUI
- **Model Management** - Easy download and management of AI models
- **Dark Mode Toggle** - Switch between light and dark themes

## 📋 Requirements

- Python 3.8 or higher
- Windows 10/11 (tested on Windows 10)
- At least 4GB RAM (8GB recommended for large PDFs)
- 2GB free disk space for models

## 🛠️ Installation

### 1. Install Python Dependencies

```bash
# Navigate to the project directory
cd adobeproject1

# Install all required packages
pip install -r requirements_gui.txt
```

### 2. Download AI Models (One-time setup, requires internet)

**⚠️ Important**: The AI models are too large for GitHub (>50MB). See [MODEL_SETUP.md](MODEL_SETUP.md) for detailed instructions.

#### Option A: Using the GUI (Recommended)
1. Run the GUI application
2. Go to the "Settings" tab
3. Click "Download" buttons for SBERT and Summarizer models
4. Models will be saved to `models/` directory

#### Option B: Manual Download
```python
# Download SBERT model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L12-v2')
model.save('models/sbert_model')

# Download Summarizer model (optional)
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
model_name = 'facebook/bart-large-cnn'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
model.save_pretrained('models/summarizer_model')
tokenizer.save_pretrained('models/summarizer_model')
```

## 🎯 How to Use

### Starting the Application

```bash
python main_gui.py
```

### Using Each Tab

#### 1. Outline Extractor Tab
- **Purpose**: Extract structured document outlines using font analysis
- **Best for**: Documents with clear heading hierarchy
- **Steps**:
  1. Click "Select PDF Files" to choose your documents
  2. Optionally select an output directory
  3. Click "Extract Outlines"
  4. View results in the text area

#### 2. Persona Insights Tab
- **Purpose**: Extract relevant sections based on specific personas and job requirements
- **Best for**: Research, analysis, and targeted information extraction
- **Steps**:
  1. Select PDF files
  2. Choose a `persona.json` file (see format below)
  3. Select SBERT model directory
  4. Optionally select summarizer model
  5. Click "Extract Insights"

#### 3. Semantic Outline Tab
- **Purpose**: Create semantic document outlines using AI embeddings
- **Best for**: Complex documents with semantic relationships
- **Steps**:
  1. Select PDF files
  2. Choose SBERT model directory
  3. Click "Extract Semantic Outlines"

#### 4. Settings Tab
- **Purpose**: Manage AI models and view application information
- **Features**:
  - Download AI models
  - View application documentation
  - Check model status

## 📄 Persona JSON Format

For the Persona Insights tab, create a `persona.json` file with this structure:

```json
{
  "persona": "PhD Researcher in Computational Biology",
  "job_to_be_done": "Prepare a literature review focusing on methodologies, datasets, and performance benchmarks"
}
```

Example personas:
- **Academic Researcher**: "Extract key findings, methodologies, and research gaps"
- **Business Analyst**: "Identify market trends, competitive analysis, and strategic insights"
- **Legal Professional**: "Find relevant regulations, compliance requirements, and legal precedents"
- **Technical Writer**: "Extract technical specifications, procedures, and documentation needs"

## 📁 Output Structure

The application creates organized output directories:

```
adobeproject1/
├── outline_extractor/output/          # Outline extraction results
├── persona_insight_extractor/output/  # Persona insights results
├── semantic_outline_extractor/output/ # Semantic outline results
└── models/                           # Downloaded AI models
    ├── sbert_model/
    └── summarizer_model/
```

## 🔧 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure all dependencies are installed: `pip install -r requirements_gui.txt`

2. **"Model not found" errors**
   - Download models using the Settings tab
   - Check that model directories contain required files
   - See [MODEL_SETUP.md](MODEL_SETUP.md) for detailed instructions

3. **Memory errors with large PDFs**
   - Close other applications
   - Process PDFs in smaller batches
   - Consider using Outline Extractor for very large documents

4. **GUI not responding**
   - Extraction runs in background threads
   - Check the status bar for progress updates
   - Large files may take several minutes

5. **Large file warnings in Git**
   - These are normal and expected
   - Models are intentionally excluded from Git due to size
   - Follow the model setup guide to download locally

### Performance Tips

- **For large documents**: Use Outline Extractor first
- **For research papers**: Use Persona Insights with academic personas
- **For technical documents**: Use Semantic Outline for better structure understanding
- **Batch processing**: Process multiple similar documents together

## 🎨 Customization

### Styling
The GUI uses the 'clam' theme by default. You can customize the appearance by modifying the style settings in `main_gui.py`.

### Adding New Extractors
To add new extraction methods:
1. Create your extractor module
2. Add a new tab in the GUI
3. Implement the extraction logic
4. Add to the requirements file

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the [MODEL_SETUP.md](MODEL_SETUP.md) guide for model-related issues
3. Review the individual extractor READMEs in their respective folders
4. Ensure all dependencies are correctly installed
5. Verify AI models are properly downloaded

## 🔄 Updates

To update the application:
1. Pull the latest code
2. Reinstall dependencies: `pip install -r requirements_gui.txt --upgrade`
3. Re-download models if new versions are available

---

**Note**: This application is designed to work completely offline after initial setup. All AI processing happens locally on your machine, ensuring privacy and security of your documents. 