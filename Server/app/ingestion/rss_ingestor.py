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

def ingest_rss(feed_url, category="General"):
    """
    Fetches news from RSS, generates embeddings, and saves to DynamoDB and ChromaDB.
    """
    print(f"Starting ingestion for [{category}] from {feed_url}...")
    feed = feedparser.parse(feed_url)
    
    count = 0
    # Process up to 10 entries per feed to keep it fast
    for entry in feed.entries: 
        news_id = generate_id(entry.link)
        
        # 1. Check if already exists in DynamoDB
        if NewsItem.get_by_id(news_id):
            continue
            
        print(f"  - New item: {entry.title[:50]}...")
        
        # 2. Generate Embeddings
        content_text = entry.title + " " + getattr(entry, 'summary', '')
        embedding = get_embeddings(content_text)
        
        # 3. Save to DynamoDB
        news_data = NewsItemSchema(
            news_id=news_id,
            title=entry.title,
            content=getattr(entry, 'summary', entry.title),
            source=getattr(entry, 'source', {'title': 'Source'}).get('title', 'Source'),
            published_at=datetime.utcnow(),
            category=category,  # Use the passed category
            embedding_id=news_id
        )
        
        if NewsItem.create(news_data):
            # 4. Save to ChromaDB
            news_collection.add(
                embeddings=[embedding],
                documents=[news_data.content],
                metadatas=[{
                    "title": news_data.title, 
                    "source": news_data.source,
                    "category": category # Add category to vector metadata
                }],
                ids=[news_id]
            )
            count += 1
            
    print(f"  Added {count} new items for {category}.")
    return count

if __name__ == "__main__":
    ingest_rss()