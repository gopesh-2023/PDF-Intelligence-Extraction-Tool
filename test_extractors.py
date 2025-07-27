#!/usr/bin/env python3
"""
Test script to check if extractors work independently
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_outline_extractor():
    print("Testing outline extractor...")
    try:
        from outline_extractor.extractor import extract_outline_from_file
        print("✅ Outline extractor import successful")
        return True
    except Exception as e:
        print(f"❌ Outline extractor import failed: {e}")
        return False

def test_persona_extractor():
    print("Testing persona extractor...")
    try:
        from persona_insight_extractor.extractor_1b import extract_persona_insight_from_file
        print("✅ Persona extractor import successful")
        return True
    except Exception as e:
        print(f"❌ Persona extractor import failed: {e}")
        return False

def test_semantic_extractor():
    print("Testing semantic extractor...")
    try:
        from semantic_outline_extractor.main import extract_semantic_outline_from_file
        print("✅ Semantic extractor import successful")
        return True
    except Exception as e:
        print(f"❌ Semantic extractor import failed: {e}")
        return False

def test_dependencies():
    print("Testing dependencies...")
    
    # Test PyMuPDF
    try:
        import fitz
        print("✅ PyMuPDF (fitz) available")
    except ImportError:
        print("❌ PyMuPDF (fitz) not available")
        return False
    
    # Test sklearn
    try:
        from sklearn.cluster import KMeans
        print("✅ sklearn available")
    except ImportError:
        print("❌ sklearn not available")
        return False
    
    # Test numpy
    try:
        import numpy as np
        print("✅ numpy available")
    except ImportError:
        print("❌ numpy not available")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Extractor Test Results ===\n")
    
    deps_ok = test_dependencies()
    print()
    
    if deps_ok:
        outline_ok = test_outline_extractor()
        persona_ok = test_persona_extractor()
        semantic_ok = test_semantic_extractor()
        
        print(f"\n=== Summary ===")
        print(f"Outline: {'✅' if outline_ok else '❌'}")
        print(f"Persona: {'✅' if persona_ok else '❌'}")
        print(f"Semantic: {'✅' if semantic_ok else '❌'}")
    else:
        print("❌ Dependencies missing - cannot test extractors") 