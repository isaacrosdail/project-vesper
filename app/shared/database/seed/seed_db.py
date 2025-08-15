# Basic script to seed our db with dummy data for demo purposes

from app._infra.database import with_db_session
from app.modules.habits.models import Habit
from app.modules.tasks.models import Tag, Task


# Seed appropriate datasets for user type
def seed_data_for(session, user):
    session.flush() # make sure we have user.id
    if user.is_owner or user.is_admin:
        seed_rich_data(session, user.id)
    else:
        seed_demo_data(session, user.id)


# Minimal dataset for demo users
def seed_demo_data(session, user_id):
    new_habit = Habit(
        name="guest_habit",
        user_id=user_id
    )
    new_tag = Tag(
        name="demo",
        user_id=user_id
    )
    new_habit.tags.append(new_tag)
    session.add(new_habit) # SQLAlchemy will cascade-add the tag automatically?


# Comprehensive dataset for development
def seed_rich_data(session, user_id):
    pass