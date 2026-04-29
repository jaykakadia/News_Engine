import feedparser
import ssl
import hashlib
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from app.models.news import NewsItem
from app.schemas.models import NewsItemSchema
from app.utils.embeddings import get_embeddings
from app.utils.vector_db import news_collection

# Fix for macOS SSL certificate verification issue
ssl._create_default_https_context = ssl._create_unverified_context

TRACKING_QUERY_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "mc_cid", "mc_eid"
}

def normalize_url(link: str) -> str:
    """
    Removes common tracking params so equivalent links map to one canonical URL.
    """
    parsed = urlsplit(link.strip())
    filtered_query = [
        (key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_KEYS
    ]
    canonical_query = urlencode(sorted(filtered_query))
    canonical_path = parsed.path.rstrip("/") or "/"
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), canonical_path, canonical_query, ""))

def generate_id(link: str, title: str = "", summary: str = ""):
    """
    Generates a stable ID:
    - Primary: canonical URL hash
    - Fallback: title + summary hash when URL is missing
    """
    if link:
        canonical_url = normalize_url(link)
        return hashlib.md5(canonical_url.encode()).hexdigest()
    fingerprint = f"{title.strip().lower()}|{summary.strip().lower()}"
    return hashlib.md5(fingerprint.encode()).hexdigest()


def ingest_rss(feed_url="https://news.google.com/rss", category="General"):
    """
    Fetches news from RSS, generates embeddings, and saves to DynamoDB and ChromaDB.
    """
    print(f"Starting ingestion for [{category}] from {feed_url}...")
    feed = feedparser.parse(feed_url)
    
    count = 0
    # Process up to 10 entries per feed to keep it fast
    for entry in feed.entries[:10]: 
        link = getattr(entry, "link", "")
        summary = getattr(entry, "summary", "")
        news_id = generate_id(link, entry.title, summary)
        
        # 1. Check if already exists in DynamoDB
        if NewsItem.get_by_id(news_id):
            continue
            
        print(f"  - New item: {entry.title[:50]}...")
        
        # 2. Generate Embeddings
        content_text = entry.title + " " + summary
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
    from config.config import RSS_FEEDS
    for url, cat in RSS_FEEDS:
        ingest_rss(url, cat)