from sentence_transformers import SentenceTransformer, util
from pathlib import Path

# Load model from HuggingFace by name (online)
model = SentenceTransformer('all-MiniLM-L6-v2')

def rank_sections_by_similarity(sections, query):
    section_texts = [f"{s['title']} - {s['text']}" for s in sections]
    query_embedding = model.encode(query, convert_to_tensor=True)
    section_embeddings = model.encode(section_texts, convert_to_tensor=True)

    similarities = util.pytorch_cos_sim(query_embedding, section_embeddings)[0]
    ranked = sorted(zip(similarities, sections), key=lambda x: x[0], reverse=True)
    return [s for _, s in ranked]
