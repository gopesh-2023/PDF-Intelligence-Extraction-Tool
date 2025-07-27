import re
from collections import Counter

def simple_similarity(text1, text2):
    """Simple text similarity based on word overlap"""
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def rank_sections_by_similarity(sections, query):
    """Rank sections by similarity to query using simple text matching"""
    try:
        # Calculate similarity scores
        scored_sections = []
        for section in sections:
            section_text = f"{section['title']} - {section['text']}"
            similarity = simple_similarity(query, section_text)
            scored_sections.append((similarity, section))
        
        # Sort by similarity score (descending)
        ranked = sorted(scored_sections, key=lambda x: x[0], reverse=True)
        return [section for _, section in ranked]
        
    except Exception as e:
        print(f"Error in similarity ranking: {e}")
        # Fallback: return sections in original order
        return sections
