# DB logic functions to access data

from .models import Task


# Get all tasks
def get_all_tasks(session):
    return session.query(Task).all()

# Get all tasks for given user_id
def get_user_tasks(session, user_id):
    return session.query(Task).filter(Task.user_id==user_id).all()