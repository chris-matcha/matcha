# Multi-stage build for security and size optimization
FROM python:3.11-slim-bullseye as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim-bullseye

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 matcha

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/matcha/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=matcha:matcha . .

# Create necessary directories
RUN mkdir -p uploads outputs logs instance && \
    chown -R matcha:matcha uploads outputs logs instance

# Switch to non-root user
USER matcha

# Add local bin to PATH
ENV PATH=/home/matcha/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check - use PORT environment variable
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import os, requests; requests.get(f'http://localhost:{os.environ.get(\"PORT\", \"8000\")}/health')"

# Run with gunicorn - use PORT environment variable for Railway
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120 --access-logfile - --error-logfile - app:app