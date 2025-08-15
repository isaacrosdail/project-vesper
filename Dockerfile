# =====================
# Stage 1: Builder
# =====================
# Build minified, output static/ for Flask
FROM python:3.12-slim AS builder
WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs

# Copy Node dependencies
COPY package*.json ./
RUN npm install

# Copy frontend source
COPY static_src/ ./static_src/
COPY tailwind.config.js postcss.config.js ./

# Build minified static assets -> outputs into /app/static
RUN npm run build

# =====================
# Stage 2: Runtime
# =====================
FROM python:3.12-slim
WORKDIR /app

# Install Python dependencies first for caching?
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy built static assets from builder
COPY --from=builder /app/static ./static

# Copy application code & migrations
COPY app/ ./app
COPY alembic/ ./alembic
COPY alembic.ini flask_app.py wsgi.py ./

# Create user & switch
RUN adduser --disabled-password appuser && \
    chown -R appuser:appuser /app
USER appuser

ENV FLASK_APP=flask_app.py
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]