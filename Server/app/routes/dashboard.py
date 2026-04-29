from flask import Blueprint, render_template
from app.models.news import NewsItem
from config.config import RSS_FEEDS

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
def index():
    # Fetch real news from DynamoDB
    news_items = NewsItem.list_all(limit=15)
    return render_template("index.html", news=news_items)

@dashboard_bp.route('/article/<news_id>', methods=['GET'])
def article_detail(news_id):
    item = NewsItem.get_by_id(news_id)
    if not item:
        return "Article not found", 404
    return render_template("article.html", item=item)

@dashboard_bp.route('/dashboard/', methods=['GET'])
def get_dashboard():
    # Calculate basic stats
    news_items = NewsItem.list_all(limit=100)
    
    stats = {
        "total_news": len(news_items),
        "total_sources": len(RSS_FEEDS),
        "total_categories": len(set([f[1] for f in RSS_FEEDS]))
    }
    
    return render_template("dashboard.html", stats=stats)

