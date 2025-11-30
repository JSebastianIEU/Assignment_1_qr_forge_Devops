# syntax=docker/dockerfile:1

############################################################
# Builder stage: build wheels for runtime dependencies
############################################################
FROM python:3.11-slim AS builder
WORKDIR /wheels_build

ENV PIP_NO_CACHE_DIR=1
COPY requirements.txt pyproject.toml ./

# Install build deps and create wheels for runtime requirements
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential curl ca-certificates \
	&& rm -rf /var/lib/apt/lists/* \
	&& python -m pip install --upgrade pip setuptools wheel \
	&& python -m pip wheel --wheel-dir=/wheels -r requirements.txt


############################################################
# Final stage: minimal runtime image
############################################################
FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/JSebastianIEU/Assignment_1_qr_forge_Devops"
LABEL org.opencontainers.image.description="QR Forge - FastAPI app for generating QR codes"
LABEL org.opencontainers.image.version="1.0.0"

# Create non-root user
RUN groupadd --system app && useradd --system --gid app --create-home --home-dir /home/app app

WORKDIR /app

# Copy wheels and install only runtime deps from wheels
COPY --from=builder /wheels /wheels
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
	&& rm -rf /wheels

# Copy application code
COPY . /app

# Ensure the non-root user owns the application directory and asset folders
RUN chown -R app:app /app /home/app || true

ENV PORT=8000
EXPOSE 8000

# Use non-root user
USER app

# Healthcheck to allow container orchestrators to probe readiness
HEALTHCHECK --interval=30s --timeout=5s --retries=5 CMD curl -f http://localhost:$PORT/health || exit 1

# Entrypoint: start the ASGI app (migrations run in CI/CD before deploy)
ENTRYPOINT ["/bin/sh", "-c", "uvicorn app.server:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
