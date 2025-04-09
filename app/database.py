# Centralized DB setup file

from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine

# Define DB engine
engine = create_engine('sqlite:///vesper.db', echo=True) # Echo for debugging

# Declarative base class
Base = declarative_base()

# Re-use this function in any module to get a clean session
def get_session():
    return Session(engine)