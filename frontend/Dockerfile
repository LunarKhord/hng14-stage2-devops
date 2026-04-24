FROM node:18-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./


RUN npm ci --only=production


FROM node:18-slim

WORKDIR /app

RUN useradd -m appuser && chown -R appuser:appuser /app


RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*


COPY --from=builder --chown=appuser:appuser /app/node_modules ./node_modules

COPY --chown=appuser:appuser . .

USER appuser


HEALTHCHECK --interval=30s --timeout=5s  --start-period=10s --retries=3 \
CMD curl --fail http://localhost:3000/ || exit 1

EXPOSE 3000
CMD ["node", "app.js"]