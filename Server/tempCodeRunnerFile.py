import feedparser
import ssl
# from app.models import NewsItem, db
# from app.utils.embeddings import get_embedding
# from app.utils.helpers import sanitize_text

# Fix for macOS SSL certificate verification issue
ssl._create_default_https_context = ssl._create_unverified_context

def fetch_news():
    feed = feedparser.parse("https://news.google.com/rss")
    
    news_list = []
    
    for entry in feed.entries:
        news_list.append({
            "title": entry.title,
            "link": entry.link
        })
    
    return news_list

print(fetch_news())