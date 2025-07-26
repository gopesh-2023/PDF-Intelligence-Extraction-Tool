# Model Setup Guide

## Why Models Are Not Included

The AI models used in this application are too large to be stored in GitHub (exceeding the 50MB file size limit). You need to download them separately.

## Required Models

### 1. SBERT Model (Required for Persona and Semantic Extractors)
- **Model**: `all-MiniLM-L12-v2`
- **Size**: ~86MB
- **Purpose**: Semantic text embeddings for persona insights and semantic outline extraction

### 2. Summarizer Model (Optional for Persona Extractor)
- **Model**: `facebook/bart-large-cnn`
- **Size**: ~1.6GB
- **Purpose**: Text summarization for persona insights

## How to Download Models

### Option 1: Using the GUI (Recommended)
1. Run the GUI application: `python main_gui.py`
2. Go to the "Settings" tab
3. Click "Download SBERT Model" and "Download Summarizer Model"
4. Models will be saved to the `models/` directory

### Option 2: Manual Download (Command Line)

#### Download SBERT Model:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L12-v2')
model.save('models/sbert_model')
```

#### Download Summarizer Model:
```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
model_name = 'facebook/bart-large-cnn'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
model.save_pretrained('models/summarizer_model')
tokenizer.save_pretrained('models/summarizer_model')
```

## Directory Structure After Setup

```
adobeproject1/
├── models/
│   ├── sbert_model/
│   │   ├── config.json
│   │   ├── pytorch_model.bin
│   │   ├── sentence_bert_config.json
│   │   └── ...
│   └── summarizer_model/
│       ├── config.json
│       ├── pytorch_model.bin
│       ├── tokenizer.json
│       └── ...
├── outline_extractor/
├── persona_insight_extractor/
├── semantic_outline_extractor/
└── main_gui.py
```

## Using Models in the GUI

1. **For Persona Insights**: Select the `models/sbert_model` directory as your SBERT model
2. **For Semantic Outline**: Select the `models/sbert_model` directory as your SBERT model
3. **Optional Summarizer**: Select the `models/summarizer_model` directory for enhanced persona insights

## Troubleshooting

### "Model not found" Error
- Ensure you've downloaded the models using one of the methods above
- Check that the model directories contain the required files
- Verify the path you're selecting in the GUI

### Download Fails
- Check your internet connection
- Ensure you have sufficient disk space (at least 2GB free)
- Try downloading models individually

### Large File Warnings
- These warnings are normal and expected
- The models are intentionally excluded from Git due to size
- Follow the setup guide above to download them locally

## Alternative: Use Hugging Face Hub

If you prefer to use models directly from Hugging Face Hub (requires internet):

```python
# In your code, replace local model paths with:
model = SentenceTransformer('all-MiniLM-L12-v2')  # Downloads automatically
```

**Note**: This requires an internet connection each time you run the application. 