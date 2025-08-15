from app._infra.db_base import Base
from sqlalchemy import Column, Float, Integer, String


# Daily Intention Model - to let intentions persist
class DailyIntention(Base):

    intention = Column(String(200))

# Daily Metric Model - Quantitative stuff: to store basic metrics like our daily steps counter, for example
class DailyMetric(Base):
    # Flexible, quantitative & objective
    metric_type = Column(String(50), nullable=False) # 'weight', 'steps', 'movement'
    unit = Column(String(20), nullable=False)         # 'lbs',    'steps', 'minutes'
    value = Column(Float)

class DailyCheckin(Base):
    # Fixed fields, quantitative & subjective
    stress_level = Column(Integer) # 1-10
    energy_level = Column(Integer) # 1-10
    mood = Column(Integer)   # maybe?
    # Can add more scales later
    
# Daily Reflection Model - Just the qualitative stuff, acts as centralized "day log"
class DailyReflection(Base):

    reflection = Column(String(2000))       # main reflection text
    accomplished = Column(String(1000))     # what I accomplished
    learned_today = Column(String(2000))
    highlights = Column(String(500))        # Optional, blend of "what went well? what was hard?"