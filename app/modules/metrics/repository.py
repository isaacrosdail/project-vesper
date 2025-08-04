
from .models import DailyMetric, DailyIntention
from sqlalchemy import func
from datetime import datetime, timezone

# Get all DailyMetrics of given user id
def get_user_metrics(session, user_id):
    return session.query(DailyMetric).filter(
        DailyMetric.user_id == user_id
    ).all()
    
    #return session.query(DailyMetric).all()

def get_today_intention(session):
    # Get today in UTC
    today_utc = datetime.now(timezone.utc).date()

    today_intention = session.query(DailyIntention).filter(
        func.date(DailyIntention.created_at) == today_utc
    ).first()
    
    return today_intention

def get_user_today_intention(session, user_id):
    # Get today in UTC
    today_utc = datetime.now(timezone.utc).date()

    today_intention = session.query(DailyIntention).filter(
        DailyIntention.user_id == user_id,
        func.date(DailyIntention.created_at) == today_utc
    ).first()
    
    return today_intention