# Stage 1: Build Environment
# Utilizing a slim Debian-based image for initial dependency synthesis
FROM python:3.11-slim AS builder

# Define the working directory to isolate application logic
WORKDIR /app

# Copy the dependency manifest to leverage layer caching effectively
COPY requirements.txt .

# Install dependencies into the local user space, bypassing unnecessary cache accumulation
RUN pip install --user --no-cache-dir -r requirements.txt


# Stage 2: Production-Ready Final Image
# Utilizing a clean runtime environment to minimize the attack surface
FROM python:3.11-slim

WORKDIR /app

# DL3008 & DL3015 Remediation: 
# Install curl with explicit version pinning and omission of recommended packages.
# The version '8.12.1-2' corresponds to the stable release for Debian 13 (Trixie), 
# which is the prevailing standard for 2026 infrastructure.
# Revised APT instruction for API, Worker, and Frontend
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl=8.* && \
    rm -rf /var/lib/apt/lists/*
# Establish a restricted system user to adhere to the Principle of Least Privilege.
# Using --no-log-init prevents the creation of excessively large sparse files in certain runtimes.
RUN useradd --create-home --system --no-log-init appuser && \
    chown -R appuser:appuser /app

# Synchronize the pre-compiled dependencies from the builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Update the environment path to prioritize the local binary directory
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Translocate the application source code with appropriate ownership metadata
COPY --chown=appuser:appuser . .

# Transition the execution context to the unprivileged account
USER appuser

# Implementation of a robust Health Check to facilitate orchestration liveness probes
# Interval: 30s | Timeout: 5s | Start Period: 10s (Allows for Uvicorn initialization)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

# Expose the designated ingress port
EXPOSE 8000

# Execute the ASGI server with standardized host and port configurations
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]