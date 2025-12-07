# =============================================================================
# Ipswich Story Weaver - Backend Dockerfile
# Optimized for AWS App Runner deployment
# =============================================================================

FROM python:3.11-slim

# Labels for container identification
LABEL maintainer="Ipswich Story Weaver"
LABEL description="FastAPI backend for Ipswich Story Weaver"

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Install system dependencies
# - gcc: Required for compiling some Python packages
# - libpq-dev: PostgreSQL client libraries (for asyncpg/psycopg2)
# - libxml2-dev, libxslt-dev: Required for lxml (BeautifulSoup parser)
# - curl: For healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libxml2-dev \
    libxslt-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better layer caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port 8000 (App Runner expects this)
EXPOSE 8000

# Health check for App Runner
# App Runner uses this to determine container health
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run the application with uvicorn
# --host 0.0.0.0: Listen on all interfaces (required for App Runner)
# --port 8000: Standard port for App Runner
# --workers 2: Multiple workers for better concurrency (adjust based on CPU)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
