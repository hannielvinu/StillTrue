# syntax=docker/dockerfile:1
FROM node:22-bookworm-slim AS ui
WORKDIR /ui
COPY frontend/package*.json ./
RUN --mount=type=secret,id=proxy_ca NODE_EXTRA_CA_CERTS=/run/secrets/proxy_ca npm ci --strict-ssl=true
COPY frontend/ ./
RUN npm run build
FROM python:3.12-slim AS app
WORKDIR /app
COPY backend/requirements.lock /tmp/requirements.lock
RUN --mount=type=secret,id=proxy_ca if [ -f /run/secrets/proxy_ca ]; then PIP_CERT=/run/secrets/proxy_ca pip install --no-cache-dir --require-hashes -r /tmp/requirements.lock; else pip install --no-cache-dir --require-hashes -r /tmp/requirements.lock; fi
COPY backend/app ./app
COPY --from=ui /ui/dist /frontend/dist
ENV FRONTEND_DIST=/frontend/dist CACHE_PATH=/app/.data/evidence.db
RUN useradd --uid 10001 --create-home runner && mkdir -p /app/.data && chown -R runner:runner /app
USER runner
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
