FROM python:3.12-slim
WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from the current dir to /app in the container
# Install Node dependencies and build CSS
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Create user & switch
RUN adduser --disabled-password appuser
RUN chown -R appuser:appuser /app
USER appuser

ENV FLASK_APP=app.py
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]