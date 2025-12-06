
FROM python:3.12-slim AS flask-app
WORKDIR /app

# Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app
COPY alembic/ /alembic/
COPY alembic.ini flask_app.py wsgi.py /

# Create non-root user
RUN adduser --disabled-password appuser && \
    chown -R appuser:appuser /app
USER appuser

ENV FLASK_APP=flask_app.py
EXPOSE 5000
WORKDIR /
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]