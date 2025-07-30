
from .models import DailyMetric, DailyIntention
from sqlalchemy import func
from datetime import datetime, timezone

def get_all_metrics(session):
    return session.query(DailyMetric).all()

def get_today_intention(session):
    # Get today in UTC
    today_utc = datetime.now(timezone.utc).date()

    today_intention = session.query(DailyIntention).filter(
        func.date(DailyIntention.created_at) == today_utc
    ).first()
    
    return today_intention