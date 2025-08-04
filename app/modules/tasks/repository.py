# DB logic functions to access data

from .models import Task


# Get all tasks
def get_all_tasks(session):
    return session.query(Task).all()

# Get all tasks for given user_id
def get_user_tasks(session, user_id):
    """
    Get all task entries for given user id.
    Args:
        session: SQLAlchemy Session object.
        user_id: User id to filter by.
    Returns:
        List of Task objects.
    """
    return session.query(Task).filter(Task.user_id==user_id).all()