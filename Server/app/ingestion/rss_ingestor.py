import feedparser
import ssl
import hashlib
from datetime import datetime
from app.models.news import NewsItem
from app.schemas.models import NewsItemSchema
from app.utils.embeddings import get_embeddings
from app.utils.vector_db import news_collection

# Fix for macOS SSL certificate verification issue
ssl._create_default_https_context = ssl._create_unverified_context

def generate_id(link: str):
    """Generates a unique ID from a URL."""
    return hashlib.md5(link.encode()).hexdigest()

def ingest_rss(feed_url="https://news.google.com/rss"):
    """
    Fetches news from RSS, generates embeddings, and saves to DynamoDB and ChromaDB.
    """
    print(f"Starting ingestion from {feed_url}...")
    feed = feedparser.parse(feed_url)
    
    count = 0
    for entry in feed.entries[:20]: # Limit to 20 for testing
        news_id = generate_id(entry.link)
        
        # 1. Check if already exists in DynamoDB
        if NewsItem.get_by_id(news_id):
            continue
            
        print(f"Processing: {entry.title}")
        
        # 2. Generate Embeddings
        embedding = get_embeddings(entry.title + " " + getattr(entry, 'summary', ''))
        
        # 3. Save to DynamoDB
        news_data = NewsItemSchema(
            news_id=news_id,
            title=entry.title,
            content=getattr(entry, 'summary', entry.title),
            source=getattr(entry, 'source', {'title': 'Unknown'}).get('title', 'Unknown'),
            published_at=datetime.utcnow(), # RSS date parsing can be tricky, using now for simplicity
            category="General",
            embedding_id=news_id
        )
        
        if NewsItem.create(news_data):
            # 4. Save to ChromaDB
            news_collection.add(
                embeddings=[embedding],
                documents=[news_data.content],
                metadatas=[{"title": news_data.title, "source": news_data.source}],
                ids=[news_id]
            )
            count += 1
            
    print(f"Ingestion complete. Added {count} new items.")
    return count

if __name__ == "__main__":
    ingest_rss()