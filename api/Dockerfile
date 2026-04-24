# Stage 1: Builder – install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Only copy requirements to leverage Docker cache
COPY requirements.txt .

# Install production dependencies into a user-local directory
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final image – slim and secure
FROM python:3.11-slim

WORKDIR /app

# Install curl for the HEALTHCHECK
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Create a non‑root user and change ownership of the app directory
RUN useradd -m appuser && chown -R appuser:appuser /app

# Copy installed dependencies from the builder stage,
# placing them into the user's home and fixing permissions
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Ensure the user's local bin is on PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy the application code, owned by appuser
COPY --chown=appuser:appuser . .

# Switch to the non‑root user
USER appuser

# Health check – calls the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]