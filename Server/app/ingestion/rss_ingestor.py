import feedparser
import ssl
import hashlib
import requests
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from bs4 import BeautifulSoup
from app.models.news import NewsItem
from app.schemas.models import NewsItemSchema
from app.utils.embeddings import get_embeddings
from app.utils.vector_db import news_collection
from app.ingestion.trigger_engine import check_triggers

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

def fetch_full_content(url: str) -> str:
    """
    Fetches the full article content from the original URL.
    Falls back to empty string if scraping fails.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script, style, nav, footer, header tags
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            tag.decompose()
        
        # Try common article content selectors
        article = (
            soup.find('article') or
            soup.find('div', class_='article-body') or
            soup.find('div', class_='post-content') or
            soup.find('div', class_='entry-content') or
            soup.find('div', class_='article-content') or
            soup.find('div', {'id': 'article-body'}) or
            soup.find('main')
        )
        
        if article:
            # Get all paragraphs from the article
            paragraphs = article.find_all('p')
            if paragraphs:
                return '\n\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        
        # Fallback: get all paragraphs from the page
        paragraphs = soup.find_all('p')
        content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)
        return content[:5000]  # Cap at 5000 chars to avoid huge DB entries
        
    except Exception as e:
        print(f"    Could not fetch full content: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Splits text into overlapping chunks for vector embedding.
    """
    if not text:
        return []
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start += (chunk_size - overlap)
    return chunks

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
        
        # 2. Try to fetch full article content
        full_content = ""
        if link:
            full_content = fetch_full_content(link)
        
        # Use full content if available, otherwise fall back to RSS summary (stripped of HTML)
        if full_content:
            content = full_content
        else:
            # Strip HTML from summary (Google News sends HTML lists in summary)
            content = BeautifulSoup(summary, "html.parser").get_text(separator=' ', strip=True)
        
        # 4. Save to DynamoDB
        news_data = NewsItemSchema(
            news_id=news_id,
            title=entry.title,
            content=content,
            source=getattr(entry, 'source', {'title': 'Source'}).get('title', 'Source'),
            link=link,
            published_at=datetime.utcnow(),
            category=category,
            embedding_id=news_id
        )
        
        if NewsItem.create(news_data):
            # 5. Save chunks to ChromaDB
            chunks = chunk_text(news_data.content, chunk_size=1000, overlap=200)
            if not chunks:
                chunks = [entry.title]
            
            chunk_embeddings = [get_embeddings(entry.title + " " + c) for c in chunks]
            chunk_metadatas = [{
                "title": news_data.title, 
                "source": news_data.source,
                "category": category,
                "news_id": news_id
            } for _ in chunks]
            chunk_ids = [f"{news_id}_{i}" for i in range(len(chunks))]
            
            news_collection.add(
                embeddings=chunk_embeddings,
                documents=chunks,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            # 6. Check triggers for this new article
            check_triggers(news_data)
            count += 1
            
    print(f"  Added {count} new items for {category}.")
    return count

if __name__ == "__main__":
    from config.config import RSS_FEEDS
    for url, cat in RSS_FEEDS:
        ingest_rss(url, cat)