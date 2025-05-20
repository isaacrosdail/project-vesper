# Added to be able to do this in our Dockerfile for deployment via Gunicorn:
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]

from flask_app import app