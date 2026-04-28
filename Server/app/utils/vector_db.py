import chromadb
from chromadb.config import Settings
import os

# Create a local directory for ChromaDB storage
CHROMA_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'chroma_db')

def get_chroma_client():
    """
    Initializes and returns a persistent ChromaDB client.
    """
    return chromadb.PersistentClient(path=CHROMA_DATA_PATH)

def get_or_create_collection(name="news_collection"):
    """
    Returns a collection from ChromaDB, creating it if it doesn't exist.
    """
    client = get_chroma_client()
    return client.get_or_create_collection(name=name)

# Shared client instance
chroma_client = get_chroma_client()
news_collection = get_or_create_collection()
