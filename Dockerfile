# syntax=docker/dockerfile:1

############################################################
# Stage 1: Build React SPA
############################################################
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

############################################################
# Stage 2: Build Python wheels for reproducible installs
############################################################
FROM python:3.11-slim AS python-builder
WORKDIR /wheels_build

ENV PIP_NO_CACHE_DIR=1
COPY requirements.txt pyproject.toml ./

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential curl ca-certificates \
	&& rm -rf /var/lib/apt/lists/* \
	&& python -m pip install --upgrade pip setuptools wheel \
	&& python -m pip wheel --wheel-dir=/wheels -r requirements.txt

############################################################
# Final stage: runtime image
############################################################
FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/JSebastianIEU/Assignment_1_qr_forge_Devops"
LABEL org.opencontainers.image.description="QR Forge - FastAPI app for generating QR codes"
LABEL org.opencontainers.image.version="1.0.0"

# Create non-root user
RUN groupadd --system app && useradd --system --gid app --create-home --home-dir /home/app app

WORKDIR /app

# Basic runtime deps (curl used in healthcheck)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies from wheels
COPY --from=python-builder /wheels /wheels
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
	&& rm -rf /wheels

# Copy backend code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copy built frontend assets
COPY --from=frontend-build /app/frontend/dist ./app/static-frontend

# Ensure ownership
RUN chown -R app:app /app /home/app || true

ENV PORT=8000
EXPOSE 8000

USER app

# Healthcheck to allow orchestrators to probe readiness
HEALTHCHECK --interval=30s --timeout=5s --retries=5 CMD curl -f http://localhost:$PORT/health || exit 1

# Entrypoint: start the ASGI app (migrations run in CI/CD before deploy)
ENTRYPOINT ["/bin/sh", "-c", "uvicorn app.server:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
