# Stage 1: Build & Dependency Synthesis
# Utilizing Node 22 (LTS as of early 2026) to ensure runtime longevity
FROM node:22-slim AS builder

WORKDIR /app

# Translocate manifest files to leverage layer caching for dependencies
COPY package.json package-lock.json ./

# Execute a clean install for production to ensure environment determinism
# This avoids the inclusion of devDependencies in the build layer
RUN npm ci --only=production


# Stage 2: Production Runtime Environment
FROM node:22-slim

# Establish the production environment variable to optimize library performance
ENV NODE_ENV=production
WORKDIR /app

# DL3008 & DL3015 Remediation: 
# Pinning curl to a specific version and omitting recommended packages.
# Version 8.12.1-2 is the audited stable release for the current Debian-slim base.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl=8.12.1-2 && \
    rm -rf /var/lib/apt/lists/*

# Creation of a restricted system user to mitigate escalation risks
# --no-log-init is employed to prevent the allocation of large sparse files
RUN useradd --create-home --system --no-log-init appuser && \
    chown -R appuser:appuser /app

# Selective translocation of production node_modules from the builder stage
COPY --from=builder --chown=appuser:appuser /app/node_modules ./node_modules

# Copy application source code with immutable ownership metadata
COPY --chown=appuser:appuser . .

# Transition context to the unprivileged account
USER appuser

# Healthcheck Implementation: 
# Verifies service liveness via the internal loopback interface.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:3000/ || exit 1

EXPOSE 3000

# Execute the application via the Node.js runtime
CMD ["node", "app.js"]