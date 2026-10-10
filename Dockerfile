FROM python:3.12-slim

# Non-root user
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/

# Own files as appuser
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

# HEALTHCHECK uses python (always present) — no curl/wget needed
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; r=urllib.request.urlopen('http://localhost:5000/health'); sys.exit(0 if r.status==200 else 1)"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:create_app()"]
