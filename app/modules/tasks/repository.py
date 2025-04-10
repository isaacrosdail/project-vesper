# DB logic functions to access data

from .models import Task

# Get all tasks
def get_all_tasks(session):
    return session.query(Task).all()