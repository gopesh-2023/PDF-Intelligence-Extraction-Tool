import spacy
import re
from collections import Counter
import json
import os

class SpacyMultilingualProcessor:
    def __init__(self):
        """Initialize spaCy with multilingual model"""
        self.nlp = None
        self.language_detected = None
        self.model_loaded = False
        
    def load_model(self, model_name="xx_ent_wiki_sm"):
        """Load spaCy multilingual model"""
        try:
            self.nlp = spacy.load(model_name)
            self.model_loaded = True
            print(f"[INFO] Loaded spaCy model: {model_name}")
            return True
        except OSError:
            print(f"[WARNING] Model {model_name} not found. Please install with: python -m spacy download {model_name}")
            return False
    
    def detect_language(self, text):
        """Detect the language of the text"""
        if not self.model_loaded:
            return "unknown"
        
        try:
            doc = self.nlp(text[:1000])  # Use first 1000 chars for language detection
            # spaCy doesn't have built-in language detection, so we'll use a simple heuristic
            # based on character sets and common words
            return self._simple_language_detection(text)
        except Exception as e:
            print(f"[ERROR] Language detection failed: {e}")
            return "unknown"
    
    def _simple_language_detection(self, text):
        """Simple language detection based on character patterns"""
        text_lower = text.lower()
        
        # Check for common language patterns
        if re.search(r'[а-яё]', text):
            return "russian"
        elif re.search(r'[一-龯]', text):
            return "chinese"
        elif re.search(r'[あ-んア-ン]', text):
            return "japanese"
        elif re.search(r'[가-힣]', text):
            return "korean"
        elif re.search(r'[ا-ي]', text):
            return "arabic"
        elif re.search(r'[α-ωΑ-Ω]', text):
            return "greek"
        elif re.search(r'[à-ÿÀ-Ÿ]', text):
            return "french"
        elif re.search(r'[äöüßÄÖÜ]', text):
            return "german"
        elif re.search(r'[ñáéíóúüÑÁÉÍÓÚÜ]', text):
            return "spanish"
        else:
            return "english"
    
    def extract_entities(self, text):
        """Extract named entities from text"""
        if not self.model_loaded:
            return []
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            return entities
        except Exception as e:
            print(f"[ERROR] Entity extraction failed: {e}")
            return []
    
    def extract_key_phrases(self, text, max_phrases=10):
        """Extract key phrases using spaCy's linguistic features"""
        if not self.model_loaded:
            return self._fallback_key_phrases(text, max_phrases)
        
        try:
            doc = self.nlp(text)
            phrases = []
            
            # Extract noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) >= 2:  # At least 2 words
                    phrases.append(chunk.text)
            
            # Extract named entities
            for ent in doc.ents:
                phrases.append(ent.text)
            
            # Remove duplicates and limit
            unique_phrases = list(set(phrases))
            return unique_phrases[:max_phrases]
            
        except Exception as e:
            print(f"[ERROR] Key phrase extraction failed: {e}")
            return self._fallback_key_phrases(text, max_phrases)
    
    def _fallback_key_phrases(self, text, max_phrases):
        """Fallback key phrase extraction using simple heuristics"""
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        filtered_words = [(word, freq) for word, freq in word_freq.items() 
                         if word not in stop_words and len(word) > 3]
        
        # Sort by frequency and return top phrases
        sorted_words = sorted(filtered_words, key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_phrases]]
    
    def analyze_text_structure(self, text):
        """Analyze text structure and provide insights"""
        if not self.model_loaded:
            return self._fallback_text_analysis(text)
        
        try:
            doc = self.nlp(text)
            
            analysis = {
                'sentences': len(list(doc.sents)),
                'tokens': len(doc),
                'entities': len(doc.ents),
                'noun_phrases': len(list(doc.noun_chunks)),
                'language': self.detect_language(text),
                'entity_types': Counter([ent.label_ for ent in doc.ents]),
                'key_entities': [ent.text for ent in doc.ents[:5]]  # Top 5 entities
            }
            
            return analysis
            
        except Exception as e:
            print(f"[ERROR] Text analysis failed: {e}")
            return self._fallback_text_analysis(text)
    
    def _fallback_text_analysis(self, text):
        """Fallback text analysis using simple methods"""
        sentences = len(re.split(r'[.!?]+', text))
        words = len(re.findall(r'\b\w+\b', text))
        
        return {
            'sentences': sentences,
            'tokens': words,
            'entities': 0,
            'noun_phrases': 0,
            'language': self.detect_language(text),
            'entity_types': {},
            'key_entities': []
        }
    
    def multilingual_search(self, query, text_sections, top_k=5):
        """Enhanced multilingual search using spaCy"""
        if not self.model_loaded:
            return self._fallback_search(query, text_sections, top_k)
        
        try:
            query_doc = self.nlp(query.lower())
            scored_sections = []
            
            for section in text_sections:
                section_text = f"{section.get('title', '')} {section.get('text', '')}"
                section_doc = self.nlp(section_text.lower())
                
                # Calculate similarity using spaCy's similarity method
                similarity = query_doc.similarity(section_doc)
                scored_sections.append((similarity, section))
            
            # Sort by similarity and return top results
            ranked = sorted(scored_sections, key=lambda x: x[0], reverse=True)
            return [section for _, section in ranked[:top_k]]
            
        except Exception as e:
            print(f"[ERROR] Multilingual search failed: {e}")
            return self._fallback_search(query, text_sections, top_k)
    
    def _fallback_search(self, query, text_sections, top_k):
        """Fallback search using simple text matching"""
        query_words = set(re.findall(r'\w+', query.lower()))
        scored_sections = []
        
        for section in text_sections:
            section_text = f"{section.get('title', '')} {section.get('text', '')}"
            section_words = set(re.findall(r'\w+', section_text.lower()))
            
            if query_words and section_words:
                intersection = query_words.intersection(section_words)
                similarity = len(intersection) / len(query_words.union(section_words))
            else:
                similarity = 0.0
            
            scored_sections.append((similarity, section))
        
        ranked = sorted(scored_sections, key=lambda x: x[0], reverse=True)
        return [section for _, section in ranked[:top_k]]

# Global instance
spacy_processor = SpacyMultilingualProcessor()

def initialize_spacy():
    """Initialize spaCy processor"""
    return spacy_processor.load_model()

def get_spacy_processor():
    """Get the global spaCy processor instance"""
    return spacy_processor 