# =====================
# Stage 1: Builder
# =====================
# Build minified, output static/ for Flask
# FROM python:3.12-slim AS builder
# WORKDIR /app

# # Install Node.js
# RUN apt-get update && apt-get install -y curl && \
#     curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
#     apt-get install -y nodejs

# # Copy Node dependencies to container root
# COPY package*.json /
# RUN npm install

# # Copy frontend source to /app/static_src/
# # and build.mjs to container root
# COPY app/static_src/ ./static_src/
# COPY build.mjs /

# # Build minified static assets -> outputs into /app/static
# WORKDIR /
# RUN npm run build
# ## might not need this one below
# WORKDIR /app

# # DEBUG: Let's see what actually exists
# RUN echo "=== PWD ===" && pwd
# RUN echo "=== LS -LA ===" && ls -la
# RUN echo "=== FIND STATIC ===" && find . -name "*static*" -type d
# RUN echo "=== FIND JS/CSS FILES ===" && find . -name "*.js" -o -name "*.css" | head -10

# # Debug: see what actually got built
# RUN ls -la /app/ && find /app -name "*.css" -o -name "*.js" | head -10

# RUN echo "=== CONTENTS OF /app/static IN BUILDER ===" && \
#     find /app/static -type f && \
#     ls -lh /app/static/js/bundle.js && \
#     ls -lh /app/static/css/app.css
# =====================
# Stage 2: Runtime
# =====================
FROM python:3.12-slim AS flask-app
WORKDIR /app

# Install Python dependencies to root
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code & migrations
COPY app/ /app
COPY alembic/ /alembic/
COPY alembic.ini flask_app.py wsgi.py /

# Copy built static assets from builder
# From /app/static to /app/static
# COPY --from=builder /app/static ./static #####

# Create user & switch
RUN adduser --disabled-password appuser && \
    chown -R appuser:appuser /app
USER appuser

######## RUN echo "=== CONTENTS OF /app/static AFTER COPY ===" && \
#     find /app/static -type f

ENV FLASK_APP=flask_app.py
EXPOSE 5000
WORKDIR /
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]


# =====================
# Stage 3: NGINX Static Server
# =====================
# FROM nginx:alpine AS static-server

# # Copy static files from the builder
# COPY --from=builder /app/static /usr/share/nginx/html

# # Copy nginx config INTO container
# # Overwrites Nginx's default config with ours
# COPY nginx/nginx.conf /etc/nginx/nginx.conf