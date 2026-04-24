# Stage 1: Dependency Synthesis (Builder)
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
# Install dependencies into the local user space to minimize image bloat
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Hardened Runtime
FROM python:3.13-slim
WORKDIR /app

# Environmental Hardening
ENV PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Resilient APT: Major version pinning to bypass Debian repository volatility (Exit 100)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl="8.*" && \
    rm -rf /var/lib/apt/lists/*

# Principle of Least Privilege: Restricted System User
RUN useradd --create-home --system --no-log-init appuser && \
    chown -R appuser:appuser /app

# Translocate pre-compiled artifacts from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

USER appuser

# Network Ingress Validation
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]