#!/usr/bin/env python3
"""
Script to install spaCy multilingual model for the PDF viewer
"""

import subprocess
import sys
import os

def install_spacy_model():
    """Install the spaCy multilingual model"""
    print("🌍 Installing spaCy multilingual model...")
    
    try:
        # Install the multilingual model
        result = subprocess.run([
            sys.executable, "-m", "spacy", "download", "xx_ent_wiki_sm"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ spaCy multilingual model installed successfully!")
            print("Model: xx_ent_wiki_sm (multilingual NER)")
            print("Size: ~50MB")
            print("Languages: 55+ languages supported")
            return True
        else:
            print(f"❌ Failed to install spaCy model:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing spaCy model: {e}")
        return False

def test_spacy_installation():
    """Test if spaCy is working correctly"""
    print("\n🧪 Testing spaCy installation...")
    
    try:
        import spacy
        
        # Try to load the model
        nlp = spacy.load("xx_ent_wiki_sm")
        
        # Test with a simple multilingual text
        test_text = "Hello world! Bonjour le monde! Hola mundo!"
        doc = nlp(test_text)
        
        print("✅ spaCy is working correctly!")
        print(f"✅ Model loaded: {nlp.meta['name']}")
        print(f"✅ Test text processed: {len(doc)} tokens")
        
        return True
        
    except Exception as e:
        print(f"❌ spaCy test failed: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 spaCy Multilingual Model Installer")
    print("=" * 40)
    
    # Check if spaCy is installed
    try:
        import spacy
        print("✅ spaCy is already installed")
    except ImportError:
        print("❌ spaCy is not installed. Please install it first:")
        print("   pip install spacy")
        return False
    
    # Install the model
    if install_spacy_model():
        # Test the installation
        if test_spacy_installation():
            print("\n🎉 Installation completed successfully!")
            print("\nYou can now use the multilingual features in your PDF viewer:")
            print("- Language detection")
            print("- Named entity recognition")
            print("- Key phrase extraction")
            print("- Multilingual text analysis")
            return True
        else:
            print("\n⚠️  Model installed but test failed. Please check your installation.")
            return False
    else:
        print("\n❌ Installation failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 