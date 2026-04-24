# Stage 1: Builder – install production dependencies
FROM node:18-slim AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Final image – slim and secure
FROM node:18-slim

WORKDIR /app

# Install curl with pinned version and --no-install-recommends
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl=7.88.1-* && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser && chown -R appuser:appuser /app

COPY --from=builder --chown=appuser:appuser /app/node_modules ./node_modules
COPY --chown=appuser:appuser . .

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:3000/health || exit 1

EXPOSE 3000
CMD ["node", "app.js"]