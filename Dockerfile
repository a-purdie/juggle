FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files 
COPY source/ ./source/

# Create assets directory in the expected location
RUN mkdir -p ./assets

# Copy assets to the assets directory that Dash expects by default
COPY source/assets/ ./assets/

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (Cloud Run uses PORT env variable)
EXPOSE 8080

# Use gunicorn for production with proper environment variables
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 source.app:server