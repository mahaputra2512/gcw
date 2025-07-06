# Twitter Hoax Detector - Dockerfile
# Multi-stage build untuk optimasi ukuran image

# =============================================================================
# Stage 1: Build Dependencies
# =============================================================================
FROM python:3.11-slim as builder

LABEL maintainer="Twitter Hoax Detector Team"
LABEL description="AI-powered Twitter hoax detection system"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.11-slim as runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Create directories
RUN mkdir -p /app/reports /app/visualizations /app/static /app/templates /app/logs && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Install additional system packages for visualization
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "run.py", "both"]

# =============================================================================
# Multi-service Dockerfile (Alternative)
# =============================================================================

# Build for web service only
FROM runtime as web
EXPOSE 8000
CMD ["python", "run.py", "web"]

# Build for telegram bot only  
FROM runtime as telegram
CMD ["python", "run.py", "telegram"]

# =============================================================================
# Development Dockerfile
# =============================================================================
FROM runtime as development

USER root

# Install development dependencies
RUN pip install \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    jupyter \
    && rm -rf /root/.cache/pip

# Install system packages for development
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    git \
    && rm -rf /var/lib/apt/lists/*

USER appuser

# Development command with auto-reload
CMD ["python", "run.py", "web", "--reload"]

# =============================================================================
# Production Dockerfile
# =============================================================================
FROM runtime as production

# Copy production configuration
COPY --chown=appuser:appuser docker/production.env .env

# Use gunicorn for production
RUN pip install gunicorn

# Production command
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"] 