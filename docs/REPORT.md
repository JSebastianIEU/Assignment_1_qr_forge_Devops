# Configuration and Deployment Report – QR Forge (DevOps Assignment)

Author: [Your Name]  
Date: [Current Date]

## 1. Azure Infrastructure

### 1.1 Azure Container Registry (ACR)
- Created ACR `jsebastianacr` (RG: `BCSAI2025-DEVOPS-STUDENTS-A`, Region: West Europe, SKU: Basic B1).
- Admin user enabled for direct auth; login server: `jsebastianacr.azurecr.io`.

### 1.2 Azure Web App for Containers
- Web App name: `jsebastianqrapp` (Linux, Region: West Europe, Plan: `ASP-jsebastianqrapp`, SKU: Basic B1).
- Deployment source: ACR `jsebastianacr`, image `qr-app`, tag `latest`, startup port 80.
- Public URL: `https://jsebastianqrapp.azurewebsites.net` (or the regional host if provided by Azure).

### 1.3 Identity and ACR Pull
- User Assigned Managed Identity: `ua-id-92af` (RG: `BCSAI2025-DEVOPS-STUDENTS-A`).
- Assigned to the Web App and granted `AcrPull` on `jsebastianacr` to pull images securely without embedded credentials.

## 2. Application Settings (App Service)
Configured in Web App → Configuration → Application Settings:

| Key | Value |
| --- | ----- |
| `SECRET_KEY` | (secure value) |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` |
| `POSTGRES_URL` | `postgresql://qradmin:JSebastian2004*@jsebastianqrdb.postgres.database.azure.com:5432/postgres` |
| `DATABASE_URL` | `sqlite:////home/app/data/qrcodes.db` (fallback) |
| `QR_ASSETS_DIR` | `/home/app/data/qr_assets` |
| `QR_TEMP_DIR` | `/home/app/data/qr_temp` |
| `PYTHONUNBUFFERED` | `1` |
| `WEBSITES_ENABLE_APP_SERVICE_STORAGE` | `false` |

Writable paths are under `/home/app/data` to allow SVG/PNG generation and local SQLite fallback.

## 3. CI/CD Overview

- **CI (`.github/workflows/ci.yaml`)**: Python 3.11, installs deps (runtime + dev), runs ruff/black checks, pytest with coverage, builds a test image, runs Trivy scan, and performs a container smoke test with a writable SQLite URL.
- **CD (`.github/workflows/cd.yaml`)**: On push to `main` or manual trigger. Builds/pushes image to ACR, sets `POSTGRES_URL` on the Web App, runs Alembic migrations inside the built image, deploys the image, smoke-tests `/health`, and verifies production URL resolved from Azure CLI.

## 4. Container and Runtime

- Dockerfile is multi-stage, non-root `app` user, healthcheck enabled. Entry point runs `uvicorn app.server:app` (migrations handled in CD).
- Default writable locations: DB at `~/data/qrcodes.db`, assets at `~/data/qr_assets`, temp at `~/data/qr_temp` (override via env vars above).

## 5. How to run locally

```bash
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
# UI: http://127.0.0.1:8000/ | Docs: http://127.0.0.1:8000/docs
```

To run with Postgres locally:
```bash
export POSTGRES_URL="postgresql://user:pass@host:5432/dbname"
uvicorn app.main:app --reload
```

## 6. Alembic migrations

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
CD also runs `alembic upgrade head` using the built image and `POSTGRES_URL` secret.

## 7. Validations performed
- All tests pass locally: `pytest` (30 tests).
- CI smoke test runs the container with `DATABASE_URL=sqlite:///tmp/qrcodes.db` to avoid permission issues.
- CD smoke test probes `/health` after deployment.

## 8. Final state
- ACR `jsebastianacr` hosting the `qr-app` image.
- Web App `jsebastianqrapp` pulling from ACR via managed identity, configured with `POSTGRES_URL` and writable asset/temp dirs.
- CI/CD pipelines operational; migrations and health checks verified in CD. 
