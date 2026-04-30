import os
from google import genai

# We use Google's advanced text-embedding model
MODEL_NAME = 'gemini-embedding-001'
# MODEL_NAME = 'gemini-embedding-2'
# MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
# MODEL_NAME = "gemini-2.0-flash-exp-text-embedding-preview-09-2025"

def get_embeddings(text: str):
    """
    Generates a vector embedding for the given text.
    Returns a list of floats.
    """
    if not text:
        return []
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not set. Cannot generate embeddings.")
        return []
        
    client = genai.Client(api_key=api_key)
    
    # Generate embedding
    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=text
    )
    
    return response.embeddings[0].values

def get_bulk_embeddings(texts: list):
    """
    Generates embeddings for a list of texts.
    """
    if not texts:
        return []
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not set. Cannot generate embeddings.")
        return []
        
    client = genai.Client(api_key=api_key)
    
    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=texts
    )
    
    return [e.values for e in response.embeddings]
