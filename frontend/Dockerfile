FROM node:22-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:22-slim
WORKDIR /app
ENV NODE_ENV=production

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl="8.*" && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --system appuser && chown -R appuser:appuser /app
COPY --from=builder --chown=appuser:appuser /app/node_modules ./node_modules
COPY --chown=appuser:appuser . .

USER appuser
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:3000/ || exit 1

EXPOSE 3000
CMD ["node", "app.js"]