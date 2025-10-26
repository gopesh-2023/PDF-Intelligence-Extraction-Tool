#!/usr/bin/env python3
"""
Enhanced CLI Handler for PDF Agent
Provides real PDF processing commands and system management
"""

import sys
import os
import json
import requests
import subprocess
from pathlib import Path

# API Configuration
API_BASE_URL = "http://127.0.0.1:5000"

def check_api_status():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("[OK] API Server Status:")
            print(f"   Status: {health['status']}")
            print(f"   Outline Extractor: {health['outline_extractor']}")
            print(f"   Persona Extractor: {health['persona_extractor']}")
            print(f"   Semantic Extractor: {health['semantic_extractor']}")
            print(f"   spaCy Multilingual: {health.get('spacy_multilingual', 'unknown')}")
            return True
        else:
            print(f"[ERROR] API Server Error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Cannot connect to API server: {e}")
        print("   Make sure the API server is running with: python api_server.py")
        return False

def extract_pdf_outline(pdf_path):
    """Extract outline from PDF using API"""
    if not os.path.exists(pdf_path):
        print(f"[ERROR] File not found: {pdf_path}")
        return False
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'pdf': f}
            response = requests.post(f"{API_BASE_URL}/api/outline", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'error' in result:
                print(f"[ERROR] {result['error']}")
                return False
            else:
                print("[OK] Outline Extraction Successful!")
                print(f"   Title: {result.get('title', 'Unknown')}")
                print(f"   Headings: {len(result.get('outline', []))}")
                print("\n[INFO] Outline:")
                for item in result.get('outline', [])[:10]:  # Show first 10
                    print(f"   {item['level']}: {item['text']} (Page {item['page']})")
                return True
        else:
            print(f"[ERROR] API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def extract_persona_insights(pdf_path, persona="PDF Analyst", job="Extract key insights"):
    """Extract persona-based insights from PDF using API"""
    if not os.path.exists(pdf_path):
        print(f"[ERROR] File not found: {pdf_path}")
        return False
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'pdf': f}
            data = {'persona': json.dumps({"persona": persona, "job_to_be_done": job})}
            response = requests.post(f"{API_BASE_URL}/api/persona", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'error' in result:
                print(f"[ERROR] {result['error']}")
                return False
            else:
                print("[OK] Persona Analysis Successful!")
                print(f"   Document: {result.get('metadata', {}).get('document', 'Unknown')}")
                print(f"   Persona: {result.get('metadata', {}).get('persona', 'Unknown')}")
                print(f"   Top Sections: {len(result.get('sections', []))}")
                print("\n[INFO] Top Insights:")
                for i, section in enumerate(result.get('sections', [])[:5]):
                    print(f"   {i+1}. {section['section_title']} (Page {section['page']})")
                return True
        else:
            print(f"[ERROR] API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def extract_semantic_outline(pdf_path):
    """Extract semantic outline from PDF using API"""
    if not os.path.exists(pdf_path):
        print(f"[ERROR] File not found: {pdf_path}")
        return False
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'pdf': f}
            response = requests.post(f"{API_BASE_URL}/api/semantic-outline", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'error' in result:
                print(f"[ERROR] {result['error']}")
                return False
            else:
                print("[OK] Semantic Outline Extraction Successful!")
                print(f"   Title: {result.get('title', 'Unknown')}")
                print(f"   Semantic Headings: {len(result.get('outline', []))}")
                print("\n[INFO] Semantic Outline:")
                for item in result.get('outline', [])[:10]:  # Show first 10
                    print(f"   {item['level']}: {item['text']} (Page {item['page']})")
                return True
        else:
            print(f"[ERROR] API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def list_pdfs():
    """List available PDF files in the project"""
    pdf_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    
    if pdf_files:
        print("[PDF] Available PDF files:")
        for pdf in pdf_files:
            size = os.path.getsize(pdf) / (1024 * 1024)  # MB
            print(f"   {pdf} ({size:.1f} MB)")
    else:
        print("[PDF] No PDF files found in the project directory")

def show_help():
    """Show available commands"""
    print("""
[INFO] Available Commands:

[System Commands]
  status          - Check API server status
  help            - Show this help message
  list-pdfs       - List available PDF files
  clear           - Clear the terminal display

[spaCy Multilingual Commands]
  install-spacy   - Install spaCy multilingual model
  test-spacy      - Test spaCy installation

Examples:
  status
  list-pdfs
  clear
  install-spacy
  test-spacy
""")

def install_spacy_model():
    """Install spaCy multilingual model"""
    print("[INFO] Installing spaCy multilingual model...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "spacy", "download", "xx_ent_wiki_sm"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] spaCy multilingual model installed successfully!")
            print("   Model: xx_ent_wiki_sm (multilingual NER)")
            print("   Size: ~50MB")
            print("   Languages: 55+ languages supported")
            return True
        else:
            print(f"[ERROR] Failed to install spaCy model:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"[ERROR] Error installing spaCy model: {e}")
        return False

def test_spacy_installation():
    """Test spaCy installation"""
    print("[INFO] Testing spaCy installation...")
    try:
        import spacy
        nlp = spacy.load("xx_ent_wiki_sm")
        
        test_text = "Hello world! Bonjour le monde! Hola mundo!"
        doc = nlp(test_text)
        
        print("[OK] spaCy is working correctly!")
        print(f"   Model: {nlp.meta['name']}")
        print(f"   Test tokens: {len(doc)}")
        return True
    except Exception as e:
        print(f"[ERROR] spaCy test failed: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("[ERROR] No command provided. Use 'help' to see available commands.")
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        show_help()
    
    elif command == "status":
        check_api_status()
    
    elif command == "list-pdfs":
        list_pdfs()
    
    elif command == "clear":
        print("__CLEAR_TERMINAL__")
    
    elif command == "install-spacy":
        install_spacy_model()
    
    elif command == "test-spacy":
        test_spacy_installation()
    
    else:
        print(f"[ERROR] Unknown command: {command}")
        print("   Use 'help' to see available commands")

if __name__ == "__main__":
    main()
