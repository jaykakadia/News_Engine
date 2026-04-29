from flask import Blueprint, render_template, session
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from app.models.news import NewsItem
from app.models.trigger import Trigger
from config.config import RSS_FEEDS
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
def index():
    # Fetch real news from DynamoDB
    news_items = NewsItem.list_all(limit=30)
    return render_template("index.html", news=news_items)

@dashboard_bp.route('/article/<news_id>', methods=['GET'])
def article_detail(news_id):
    item = NewsItem.get_by_id(news_id)
    if not item:
        return "Article not found", 404
    return render_template("article.html", item=item)

@dashboard_bp.route('/dashboard/', methods=['GET'])
def get_dashboard():
    # Fetch data
    news_items = NewsItem.list_all(limit=500)
    categories = sorted(list(set([f[1] for f in RSS_FEEDS])))
    
    # Count triggers for current user
    user_id = session.get('user_id') or session.get('tenant_id', '')
    triggers = Trigger.get_by_user(user_id) if user_id else []
    
    # Category distribution
    category_counts = Counter(item.category for item in news_items)
    
    # Trend data: articles per day for last 7 days
    today = datetime.utcnow().date()
    trend = defaultdict(lambda: defaultdict(int))
    for item in news_items:
        item_date = item.published_at.date() if hasattr(item.published_at, 'date') else today
        days_ago = (today - item_date).days
        if days_ago <= 6:
            date_str = item_date.strftime('%b %d')
            trend[date_str][item.category] += 1
    
    # Build ordered labels for the last 7 days
    trend_labels = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        trend_labels.append(d.strftime('%b %d'))
    
    # Build datasets per category
    trend_datasets = {}
    for cat in categories:
        trend_datasets[cat] = [trend[label].get(cat, 0) for label in trend_labels]
    
    stats = {
        "total_news": len(news_items),
        "total_sources": len(RSS_FEEDS),
        "total_categories": len(categories),
        "categories": categories,
        "recent_triggers": len(triggers),
        "category_counts": json.dumps(dict(category_counts)),
        "trend_labels": json.dumps(trend_labels),
        "trend_datasets": json.dumps(trend_datasets)
    }
    
    return render_template("dashboard.html", stats=stats)
