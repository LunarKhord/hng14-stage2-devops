# Stage 1: Builder – install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final image – slim and secure
FROM python:3.11-slim

WORKDIR /app

# Create a non‑root user
RUN useradd -m appuser && chown -R appuser:appuser /app

# Copy dependencies from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non‑root user
USER appuser

# Health check – verify the worker.py process is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD pgrep -f "python.*worker.py" || exit 1

CMD ["python", "worker.py"]