from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.trigger import Trigger
from app.models.interest import Interest
from app.models.news import NewsItem
from app.schemas.models import InterestSchema
from config.config import RSS_FEEDS
import uuid

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/alerts/', methods=['GET'])
def alerts_page():
    user_id = session.get('user_id') or session.get('tenant_id')
    if not user_id:
        return redirect(url_for('auth.login_page'))
    
    triggers = Trigger.get_by_user(user_id)
    
    # Enrich triggers with news article details
    enriched = []
    for t in triggers:
        news = NewsItem.get_by_id(t.news_id)
        enriched.append({
            'trigger': t,
            'news': news
        })
    
    return render_template("alerts.html", alerts=enriched)

@alerts_bp.route('/alerts/read/<trigger_id>', methods=['POST'])
def mark_read(trigger_id):
    Trigger.mark_as_read(trigger_id)
    return redirect(url_for('alerts.alerts_page'))

@alerts_bp.route('/interests/', methods=['GET'])
def interests_page():
    user_id = session.get('user_id') or session.get('tenant_id')
    if not user_id:
        return redirect(url_for('auth.login_page'))
    
    interest = Interest.get_by_user(user_id)
    categories = sorted(list(set([f[1] for f in RSS_FEEDS])))
    
    return render_template("interests.html", interest=interest, all_categories=categories)

@alerts_bp.route('/interests/', methods=['POST'])
def save_interests():
    user_id = session.get('user_id') or session.get('tenant_id')
    if not user_id:
        return redirect(url_for('auth.login_page'))
    
    keywords_raw = request.form.get('keywords', '')
    keywords = [k.strip() for k in keywords_raw.split(',') if k.strip()]
    categories = request.form.getlist('categories')
    
    existing = Interest.get_by_user(user_id)
    
    if existing:
        Interest.update(existing.interest_id, keywords, categories)
        flash("Interests updated successfully!", "success")
    else:
        interest_data = InterestSchema(
            interest_id=str(uuid.uuid4()),
            user_id=user_id,
            keywords=keywords,
            categories=categories
        )
        Interest.create(interest_data)
        flash("Interests saved successfully!", "success")
    
    return redirect(url_for('alerts.interests_page'))
