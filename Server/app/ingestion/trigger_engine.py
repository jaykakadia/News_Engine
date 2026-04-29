"""
Trigger Engine — Matches incoming news against user interests and fires alerts.
"""
import uuid
from datetime import datetime
from app.models.interest import Interest
from app.models.trigger import Trigger
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.models import TriggerSchema
from app.utils.email_sender import send_trigger_email


def score_article(news_item, interest):
    """
    Calculates a relevance score (0-100) for a news article against a user's interests.
    
    Scoring:
        +15 points per keyword found in the article title
        +5  points per keyword found in the article content
        +20 points if the article category matches user's category interest
    """
    score = 0
    title_lower = news_item.title.lower()
    content_lower = news_item.content.lower() if news_item.content else ""
    
    # Keyword matching
    for keyword in interest.keywords:
        kw = keyword.lower().strip()
        if not kw:
            continue
        if kw in title_lower:
            score += 15
        if kw in content_lower:
            score += 5
    
    # Category matching
    for cat in interest.categories:
        if cat.lower().strip() == news_item.category.lower().strip():
            score += 20
            break  # Only count category once
    
    return min(score, 100)


def _get_user_email_and_name(user_id):
    """Look up a user's email and name from either Users or Tenants table."""
    user = User.get_by_id(user_id)
    if user:
        return user.email, user.name
    
    tenant = Tenant.get_by_id(user_id)
    if tenant:
        return tenant.email, tenant.name
    
    return None, None


def check_triggers(news_item):
    """
    Checks a newly ingested news item against ALL users' interests.
    If the relevance score meets the threshold (>= 50), a trigger is created
    and an email alert is sent.
    """
    all_interests = Interest.list_all()
    triggers_created = 0
    
    for interest in all_interests:
        score = score_article(news_item, interest)
        
        if score >= 50:
            trigger_data = TriggerSchema(
                trigger_id=str(uuid.uuid4()),
                user_id=interest.user_id,
                news_id=news_item.news_id,
                score=float(score),
                sent=False,
                created_at=datetime.utcnow()
            )
            
            if Trigger.create(trigger_data):
                triggers_created += 1
                print(f"    🔔 Trigger fired! User={interest.user_id[:8]}... Score={score} for '{news_item.title[:40]}...'")
                
                # Send email alert
                email, name = _get_user_email_and_name(interest.user_id)
                if email:
                    article_link = getattr(news_item, 'link', '')
                    send_trigger_email(email, name, news_item.title, score, article_link)
    
    return triggers_created

