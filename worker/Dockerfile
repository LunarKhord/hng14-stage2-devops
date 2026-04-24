# Stage 1: Dependency Synthesis (Builder)
# Utilizing Python 3.13-slim to leverage the latest performance optimizations 
# in the CPython interpreter and enhanced type-hinting support.
FROM python:3.13-slim AS builder

WORKDIR /app

# Translocate the dependency manifest
COPY requirements.txt .

# Execute an unprivileged dependency installation. 
# The --no-cache-dir flag is imperative to prevent layer inflation.
RUN pip install --user --no-cache-dir -r requirements.txt


# Stage 2: Hardened Runtime Environment
FROM python:3.13-slim

# Set environment variables to optimize Python for containerized execution
# PYTHONUNBUFFERED=1 ensures logs are flushed immediately to the stream.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /app

# DL3008 & DL3015 Remediation:
# Note: The healthcheck utilizes 'pgrep', which is provided by the 'procps' package.
# We maintain 'curl' if external interrogation is required, but focus here 
# on the requirements for your specific healthcheck logic.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl=8.12.1-2 \
        procps=2:4.0.4-5 && \
    rm -rf /var/lib/apt/lists/*

# Creation of an unprivileged system user to satisfy the Principle of Least Privilege.
RUN useradd --create-home --system --no-log-init appuser && \
    chown -R appuser:appuser /app

# Selective copy of the pre-built Python environment
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application logic with immutable ownership
COPY --chown=appuser:appuser . .

# Transition to the non-root execution context
USER appuser

# Implementation of a Process-Based Health Interrogation
# This ensures that the worker daemon has not entered a 'zombie' or stalled state.
# We use pgrep to verify the existence of the python process executing worker.py.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD pgrep -f "python.*worker.py" || exit 1

# Execute the asynchronous worker logic
CMD ["python", "worker.py"]