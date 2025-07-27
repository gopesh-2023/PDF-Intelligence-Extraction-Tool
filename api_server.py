from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import shutil
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = tempfile.gettempdir()

# Lazy imports to handle dependency issues
def get_outline_extractor():
    try:
        from outline_extractor.extractor import extract_outline_from_file
        return extract_outline_from_file
    except ImportError as e:
        return lambda x: {"error": f"Outline extractor not available: {str(e)}"}

def get_persona_extractor():
    try:
        from persona_insight_extractor.extractor_1b import extract_persona_insight_from_file
        return extract_persona_insight_from_file
    except ImportError as e:
        return lambda x, y: {"error": f"Persona extractor not available: {str(e)}"}

def get_semantic_extractor():
    try:
        from semantic_outline_extractor.main import extract_semantic_outline_from_file
        return extract_semantic_outline_from_file
    except ImportError as e:
        return lambda x: {"error": f"Semantic extractor not available: {str(e)}"}

@app.route('/api/outline', methods=['POST'])
def extract_outline():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF uploaded'}), 400
    pdf = request.files['pdf']
    temp_pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(temp_pdf_path)
    try:
        extractor = get_outline_extractor()
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
        'semantic_extractor': 'available' if get_semantic_extractor() else 'unavailable'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 