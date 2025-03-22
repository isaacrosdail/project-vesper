# Main database setup here

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Create the engine for DB (do only once for all of Vesper)
engine = create_engine('sqlite:///vesper.db', echo=True) # Echo for debugging/learning purposes

# Re-use this function in any module to get a clean session
def get_session():
    return Session(engine)