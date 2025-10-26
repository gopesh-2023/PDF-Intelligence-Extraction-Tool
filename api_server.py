from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import shutil
import json

app = Flask(__name__)
CORS(app)

# Initialize spaCy processor
try:
    from spacy_multilingual_utils import initialize_spacy, get_spacy_processor
    spacy_initialized = initialize_spacy()
except ImportError as e:
    print(f"[WARNING] spaCy not available: {e}")
    spacy_initialized = False

UPLOAD_FOLDER = tempfile.gettempdir()

# Lazy imports to handle dependency issues
def get_outline_extractor():
    try:
        from outline_extractor.extractor import extract_outline_from_file
        return extract_outline_from_file
    except ImportError as e:
        print(f"[WARNING] Outline extractor import failed: {e}")
        return None

def get_persona_extractor():
    try:
        from persona_insight_extractor.extractor_1b import extract_persona_insight_from_file
        return extract_persona_insight_from_file
    except ImportError as e:
        print(f"[WARNING] Persona extractor import failed: {e}")
        return None

def get_semantic_extractor():
    try:
        from semantic_outline_extractor.main import extract_semantic_outline_from_file
        return extract_semantic_outline_from_file
    except ImportError as e:
        print(f"[WARNING] Semantic extractor import failed: {e}")
        return None

@app.route('/api/outline', methods=['POST'])
def extract_outline():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF uploaded'}), 400
    pdf = request.files['pdf']
    temp_pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(temp_pdf_path)
    try:
        extractor = get_outline_extractor()
        if not extractor:
            return jsonify({'error': 'Outline extractor not available on server (missing dependencies)'}), 503
        result = extractor(temp_pdf_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

@app.route('/api/persona', methods=['POST'])
def extract_persona():
    if 'pdf' not in request.files or 'persona' not in request.form:
        return jsonify({'error': 'PDF and persona required'}), 400
    pdf = request.files['pdf']
    persona_json = request.form['persona']
    try:
        persona = json.loads(persona_json)
    except Exception:
        return jsonify({'error': 'Invalid persona JSON'}), 400
    temp_pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(temp_pdf_path)
    try:
        extractor = get_persona_extractor()
        if not extractor:
            return jsonify({'error': 'Persona extractor not available on server (missing dependencies)'}), 503
        result = extractor(temp_pdf_path, persona)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

@app.route('/api/semantic-outline', methods=['POST'])
def extract_semantic_outline():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF uploaded'}), 400
    pdf = request.files['pdf']
    temp_pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(temp_pdf_path)
    try:
        extractor = get_semantic_extractor()
        if not extractor:
            return jsonify({'error': 'Semantic outline extractor not available on server (missing dependencies)'}), 503
        result = extractor(temp_pdf_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'running',
        'outline_extractor': 'available' if get_outline_extractor() else 'unavailable',
        'persona_extractor': 'available' if get_persona_extractor() else 'unavailable', 
        'semantic_extractor': 'available' if get_semantic_extractor() else 'unavailable',
        'spacy_multilingual': 'available' if spacy_initialized else 'unavailable'
    })

@app.route('/api/spacy/analyze', methods=['POST'])
def spacy_analyze():
    """Analyze text using spaCy multilingual features"""
    if not spacy_initialized:
        return jsonify({'error': 'spaCy not available'}), 503
    
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Text required'}), 400
    
    text = data['text']
    processor = get_spacy_processor()
    
    try:
        # Perform comprehensive analysis
        analysis = processor.analyze_text_structure(text)
        entities = processor.extract_entities(text)
        key_phrases = processor.extract_key_phrases(text)
        
        result = {
            'analysis': analysis,
            'entities': entities,
            'key_phrases': key_phrases,
            'language_detected': analysis['language']
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spacy/search', methods=['POST'])
def spacy_search():
    """Multilingual search using spaCy"""
    if not spacy_initialized:
        return jsonify({'error': 'spaCy not available'}), 503
    
    data = request.get_json()
    if not data or 'query' not in data or 'sections' not in data:
        return jsonify({'error': 'Query and sections required'}), 400
    
    query = data['query']
    sections = data['sections']
    top_k = data.get('top_k', 5)
    
    processor = get_spacy_processor()
    
    try:
        results = processor.multilingual_search(query, sections, top_k)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spacy/entities', methods=['POST'])
def spacy_entities():
    """Extract named entities from text"""
    if not spacy_initialized:
        return jsonify({'error': 'spaCy not available'}), 503
    
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Text required'}), 400
    
    text = data['text']
    processor = get_spacy_processor()
    
    try:
        entities = processor.extract_entities(text)
        return jsonify({'entities': entities})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 