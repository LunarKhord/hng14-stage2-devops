# Stage 1: Dependency Synthesis (Builder)
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Hardened Runtime
FROM python:3.13-slim
WORKDIR /app

# Environmental Hardening
ENV PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Resilient APT: Including procps for pgrep capability
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        procps="2:*" && \
    rm -rf /var/lib/apt/lists/*

# Restricted System User
RUN useradd --create-home --system --no-log-init appuser && \
    chown -R appuser:appuser /app

# Translocate pre-compiled artifacts
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

USER appuser

# Process Vitality Validation
# Ensures the worker.py script has not entered a zombie or stalled state.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD pgrep -f "python.*worker.py" || exit 1

# No EXPOSE directive is used as the worker does not accept ingress traffic.
CMD ["python", "worker.py"]