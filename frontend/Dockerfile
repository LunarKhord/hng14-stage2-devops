# Stage 1: Builder – install production dependencies
FROM node:18-slim AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Final image – slim and secure
FROM node:18-slim

WORKDIR /app

# Install curl for HEALTHCHECK
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Create a non‑root user and adjust ownership
RUN useradd -m appuser && chown -R appuser:appuser /app

# Copy node_modules from builder
COPY --from=builder --chown=appuser:appuser /app/node_modules ./node_modules

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to the non‑root user
USER appuser

# Health check – calls the /health endpoint you added in app.js
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:3000/health || exit 1

EXPOSE 3000

CMD ["node", "app.js"]