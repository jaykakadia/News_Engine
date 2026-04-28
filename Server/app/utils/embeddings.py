from sentence_transformers import SentenceTransformer
import os

# Initialize the model (it will download on first run)
# We use a lightweight model suitable for CPU processing
MODEL_NAME = 'all-MiniLM-L6-v2'
model = SentenceTransformer(MODEL_NAME)

def get_embeddings(text: str):
    """
    Generates a vector embedding for the given text.
    Returns a list of floats.
    """
    if not text:
        return []
    
    # Generate embedding
    embedding = model.encode(text)
    
    # Convert numpy array to list
    return embedding.tolist()

def get_bulk_embeddings(texts: list):
    """
    Generates embeddings for a list of texts.
    """
    if not texts:
        return []
    
    embeddings = model.encode(texts)
    return embeddings.tolist()
