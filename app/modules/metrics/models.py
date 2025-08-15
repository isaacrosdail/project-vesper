from sqlalchemy import Column, Float, Integer, String, Time

from app._infra.db_base import Base


class DailyIntention(Base):
    intention = Column(String(200), server_default="What's your focus today?")

    def __repr__(self):
        return f"<Intention id={self.id} text={self.intention}>"

class DailyEntry(Base):
    """Stores everything in "master" units, converts based on user preferences."""
    weight = Column(Float)          # kg
    steps = Column(Integer)         # count
    wake_time = Column(Time)        # Stores time.time(7, 30, 0)
    sleep_time = Column(Time)
    calories = Column(Integer)      # kcal

    def __repr__(self):
        return f"<DailyEntry id={self.id} created_at={self.created_at}>"
    
    @property
    def populated_metrics(self):
        """Returns list of metrics which have entries."""
        metrics = []
        metric_types = ["weight", "steps", "wake_time", "sleep_time", "calories"]
        # Get corresponding attribute for each column to see if it's populated
        # If yes, store in metrics list
        metrics = [metric_type for metric_type in metric_types if getattr(self, metric_type) is not None]
        return metrics
    
    @property
    def has_sleep_data(self):
        """True if both sleep & wake times are stored."""
        return self.sleep_time is not None and self.wake_time is not None