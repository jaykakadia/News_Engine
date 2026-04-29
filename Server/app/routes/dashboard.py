from flask import Blueprint, render_template, session, request
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from app.models.news import NewsItem
from app.models.trigger import Trigger
from app.models.user import User
from app.models.interest import Interest
from app.models.chat import ChatHistory
from config.config import RSS_FEEDS
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
def index():
    # Fetch real news from DynamoDB
    news_items = NewsItem.list_all(limit=200)
    
    # Get unique categories
    categories = sorted(list(set(item.category for item in news_items)))
    
    # Filter by category if requested
    selected_category = request.args.get('category')
    if selected_category and selected_category != 'All':
        news_items = [item for item in news_items if item.category == selected_category]
        
    return render_template("index.html", news=news_items[:50], categories=categories, selected_category=selected_category or 'All')

@dashboard_bp.route('/article/<news_id>', methods=['GET'])
def article_detail(news_id):
    item = NewsItem.get_by_id(news_id)
    if not item:
        return "Article not found", 404
    return render_template("article.html", item=item)

@dashboard_bp.route('/dashboard/', methods=['GET'])
def get_dashboard():
    # If agency, show agency dashboard
    if session.get('user_role') == 'agency':
        return _agency_dashboard()
    
    # Fetch data
    news_items = NewsItem.list_all(limit=500)
    categories = sorted(list(set([f[1] for f in RSS_FEEDS])))
    
    # Count triggers for current user
    user_id = session.get('user_id') or session.get('tenant_id', '')
    triggers = Trigger.get_by_user(user_id) if user_id else []
    
    # Get recent chats for user
    recent_chats_all = ChatHistory.get_by_user(user_id) if user_id else []
    recent_chats_all.sort(key=lambda x: x.created_at, reverse=True)
    recent_chats = []
    for chat in recent_chats_all[:3]:
        recent_chats.append({
            "query": chat.query,
            "timestamp": chat.created_at
        })
    
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
        "recent_chats": recent_chats,
        "trend_labels": json.dumps(trend_labels),
        "trend_datasets": json.dumps(trend_datasets)
    }
    
    return render_template("dashboard.html", stats=stats)


def _agency_dashboard():
    """Agency-specific dashboard with team-level analytics."""
    tenant_id = session.get('tenant_id', '')
    
    # Get all users in this agency
    team_users = User.get_by_tenant(tenant_id)
    
    # Collect all user IDs (include the agency itself)
    team_user_ids = [u.user_id for u in team_users]
    team_user_ids.append(tenant_id)
    
    # Get all interests across the team
    all_interests = []
    keyword_counter = Counter()
    category_counter = Counter()
    for uid in team_user_ids:
        interest = Interest.get_by_user(uid)
        if interest:
            all_interests.append(interest)
            for kw in interest.keywords:
                keyword_counter[kw.strip()] += 1
            for cat in interest.categories:
                category_counter[cat] += 1
    
    # Get all triggers across the team
    all_triggers = []
    trigger_per_user = Counter()
    for uid in team_user_ids:
        user_triggers = Trigger.get_by_user(uid)
        all_triggers.extend(user_triggers)
        trigger_per_user[uid] += len(user_triggers)
    
    # Find most active users (by trigger count)
    active_users = []
    for user in team_users:
        active_users.append({
            "name": user.name,
            "email": user.email,
            "trigger_count": trigger_per_user.get(user.user_id, 0)
        })
    active_users.sort(key=lambda x: x['trigger_count'], reverse=True)
    
    # News stats
    news_items = NewsItem.list_all(limit=500)
    categories = sorted(list(set([f[1] for f in RSS_FEEDS])))
    category_counts = Counter(item.category for item in news_items)
    
    stats = {
        "total_users": len(team_users),
        "total_triggers": len(all_triggers),
        "total_news": len(news_items),
        "total_categories": len(categories),
        "categories": categories,
        "top_keywords": json.dumps(dict(keyword_counter.most_common(10))),
        "interest_categories": json.dumps(dict(category_counter)),
        "category_counts": json.dumps(dict(category_counts)),
        "active_users": active_users[:10]
    }
    
    return render_template("agency_dashboard.html", stats=stats)
