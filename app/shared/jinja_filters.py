
from datetime import datetime

def prettyiso(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)

def register_filters(app):
    app.jinja_env.filters['prettyiso'] = prettyiso