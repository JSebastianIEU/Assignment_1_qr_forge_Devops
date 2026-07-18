# QR Forge

![CI](https://github.com/JSebastianIEU/qr_forge/actions/workflows/ci.yaml/badge.svg)

A free, unlimited QR code generator — FastAPI backend, React SPA frontend, packaged as a single hardened container with CI/CD, Prometheus metrics and structured logging.

Generate branded QR codes (PNG or SVG) with control over colour, padding, corner radius and size. Sign in to keep a history of everything you have generated, re-download it later, or export it as CSV.

## What is in here

- **Generator** — UI and API for building QR codes with live preview and SVG/PNG download.
- **Accounts and history** — signup/login with JWT, per-user QR history, profile management, CSV export.
- **Tests** — 124 passing pytest tests (unit + integration) at **80% line coverage**; CI fails the build under 60%.
- **CI/CD** — lint, test, coverage gate, Trivy image scan, then build and deploy to Azure Container Instances.
- **Observability** — Prometheus `/metrics`, an optional local Prometheus + Grafana stack, and structured logging.

## Deployment status

QR Forge was deployed and running on Azure — Container Instances behind an HTTPS proxy on App Service, with Postgres and Blob Storage. **That deployment has since been torn down** (the Azure credits funding it ran out), so the previously published URLs no longer resolve. The pipeline in `.github/workflows/cd.yaml` is intact and describes exactly how it was provisioned; running it against a fresh Azure subscription reproduces the environment.

To see the app, run it locally or via Docker — both are covered below.

## Run locally

**Prerequisites:** Python 3.11+, Node.js 20+, Git.

1) Clone

```bash
git clone https://github.com/JSebastianIEU/qr_forge.git
cd qr_forge
```

2) Virtual environment

```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate

# Windows PowerShell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

3) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt   # tests and linting
```

4) Environment (optional)

Everything has a working default — SQLite and local asset folders — so you can skip this. To override, create a `.env`:

```
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=720
ALGORITHM=HS256

# Database (Postgres in production; SQLite by default locally)
POSTGRES_URL=postgresql://<user>:<password>@<host>:5432/<db>
DATABASE_URL=sqlite:///./qr.db

# Asset dirs (auto-created at startup)
QR_ASSETS_DIR=./qr_assets
QR_TEMP_DIR=./qr_temp
```

5) Build the frontend

The backend serves the SPA from `src/app/static-frontend/`, which is a build artifact and is not committed. Build it once:

```bash
cd src/frontend
npm ci
npm run build
cp -r dist ../app/static-frontend
cd ../..
```

6) Run the API

The application package lives in `src/`, so point uvicorn at that directory:

```bash
uvicorn app.server:app --app-dir src --reload
```

- UI: http://127.0.0.1:8000/
- Docs: http://127.0.0.1:8000/docs
- Metrics: http://127.0.0.1:8000/metrics
- Health: http://127.0.0.1:8000/health

`app.server:app` is the canonical entrypoint — it is what the container runs. Create an account through the UI or `POST /api/auth/signup`, then try the generator, history and profile screens.

**Frontend dev server** (hot reload, proxies `/api` to port 8000) — run this instead of step 5 while working on the UI:

```bash
cd src/frontend
npm run dev
```

7) Tests

```bash
pytest src/tests                              # backend
pytest src/tests --cov=src/app --cov-report=term   # with coverage

cd src/frontend && npm test -- --run          # frontend
```

Backend tests use an in-memory SQLite database and temp asset folders, so local data is untouched.

8) Docker

The image builds the frontend itself, so this is the shortest path to a working app:

```bash
docker build -f infrastructure/docker/Dockerfile -t qr_forge .
docker run -p 8000:8000 qr_forge
```

## Project structure

```
.
├── src/
│   ├── app/                  # FastAPI application package
│   │   ├── main.py           # App factory, middleware, metrics, SPA mounts
│   │   ├── server.py         # ASGI entrypoint (uvicorn app.server:app)
│   │   ├── config.py         # Environment-driven settings
│   │   ├── db.py             # SQLModel engine + session factory
│   │   ├── models.py         # SQLModel tables (users, QR items)
│   │   ├── schemas.py        # Request/response schemas
│   │   ├── storage.py        # Local + Azure Blob asset storage backends
│   │   ├── core/             # Bootstrap, logging, security (hashing, JWT)
│   │   ├── routers/          # auth, user, qr, export
│   │   ├── services/         # QR rendering and persistence logic
│   │   └── assets/           # UI icons served at /assets
│   ├── frontend/             # React 18 + TypeScript + Tailwind SPA (Vite)
│   ├── alembic/              # Database migrations
│   ├── alembic.ini
│   └── tests/                # Pytest suite
├── infrastructure/
│   ├── docker/               # Dockerfile + HTTPS proxy images
│   └── monitoring/           # Prometheus config, Grafana dashboard, compose
├── docs/                     # REPORT.md (deployment write-up), CHANGELOG.md
├── .github/workflows/        # ci.yaml, cd.yaml
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml            # ruff + black config
```

## Key files

- `src/app/main.py` — app factory, CORS, Prometheus instrumentation, SPA and asset mounts.
- `src/app/server.py` — the ASGI entrypoint the container runs.
- `src/app/storage.py` — pluggable asset storage: local filesystem locally, Azure Blob in the cloud.
- `infrastructure/docker/Dockerfile` — three-stage build (Node SPA build → Python wheel build → slim runtime), non-root user, healthcheck.
- `infrastructure/docker/Dockerfile.https-proxy` — the TLS-terminating proxy described below.
- `.github/workflows/ci.yaml` — ruff, black, pytest + coverage gate, Docker build, Trivy scan, container smoke test.
- `.github/workflows/cd.yaml` — security scan, build, push to ACR, deploy to ACI, migrations, HTTPS proxy.
- `infrastructure/monitoring/` — Prometheus config, Grafana dashboard JSON, local compose stack.
- `docs/REPORT.md` — full deployment write-up covering the Azure resources and validation steps.

## CI / CD

**CI** (`.github/workflows/ci.yaml`) runs on every push and PR to `main`:

1. `ruff check` and `black --check`
2. Full pytest suite with coverage, emitting `coverage.xml` and `results.xml`
3. Coverage gate — `COVERAGE_GATE: 60`, enforced via `coverage report --fail-under`
4. Builds the Docker image, scans it with Trivy (CRITICAL/HIGH), boots the container and smoke-tests `/health` and `/metrics`

Measured coverage is currently 80%, comfortably above the 60% gate.

**CD** (`.github/workflows/cd.yaml`) runs on pushes to `main` and `develop`:

1. Security scan — Bandit, Safety, and Trivy with results uploaded to GitHub Security
2. Builds and tests the frontend, runs the backend suite
3. Builds the image and pushes it to Azure Container Registry (tagged with the commit SHA and `latest`)
4. Recreates the **Azure Container Instance** from the new image with all runtime configuration injected as environment variables
5. Runs `alembic upgrade head` from inside the freshly built image, so migrations always match the code being deployed
6. Smoke-tests `/health` on the ACI endpoint
7. Builds and deploys a second **HTTPS proxy container to Azure App Service**

### Why the HTTPS proxy exists

Azure Container Instances does not terminate TLS. An ACI container with a public DNS label is reachable only over plain HTTP on the port you expose — there is no managed certificate and no way to attach one directly.

That is a problem for this app: the browser blocks mixed content, the clipboard and other secure-context APIs the frontend uses are unavailable over HTTP, and shipping a login form over an unencrypted connection is not acceptable regardless.

The usual answer is Application Gateway or Front Door, both of which cost more per month than the rest of this deployment combined. Instead, the pipeline deploys a second, very small container — `infrastructure/docker/Dockerfile.https-proxy` — to Azure App Service, which *does* provide a free managed certificate on its `*.azurewebsites.net` hostname. That container reverse-proxies to the ACI backend, so users get a valid HTTPS endpoint while the application itself keeps running on cheap ACI compute.

It is a trade-off, not a free win: it adds a network hop and a second thing to deploy. But it buys real TLS for the price of a Basic App Service plan, which was the constraint that mattered here.

## Monitoring and metrics

`/metrics` exposes Prometheus-compatible counters and histograms (request count, latency, status codes).

Local observability stack, once the app is running:

```bash
docker compose -f infrastructure/monitoring/docker-compose.monitoring.yml up
```

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin), import `infrastructure/monitoring/grafana-dashboard.json`

## Logging

Structured logging is enabled by default. Set `LOG_LEVEL` (`DEBUG`, `INFO`, `WARNING`, `ERROR`) to adjust verbosity. Records include timestamp, level, module and message.

## API overview

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST | `/api/auth/signup` | Create a new user |
| POST | `/api/auth/login` | Obtain an access token |
| POST | `/api/auth/logout` | Invalidate current token (client-side) |
| GET | `/api/user/me` | Current user profile |
| PATCH | `/api/user/me` | Update full name / password |
| DELETE | `/api/user/me` | Delete account and owned QR codes |
| POST | `/api/qr/preview` | Render a QR preview without saving |
| POST | `/api/qr` | Persist a QR configuration |
| GET | `/api/qr` / `/api/qr/history` | List the current user's QR items |
| DELETE | `/api/qr/{id}` | Remove a saved QR |
| GET | `/api/qr/{id}/download?format=svg\|png` | Download saved assets |
| GET | `/api/export/csv` | Export history as CSV |

Protected routes require a bearer token (`Authorization: Bearer <token>`).

## Database migrations

Alembic manages the schema for the SQLModel models. Migration files live in `src/alembic/versions/`, and `alembic.ini` is in `src/`, so run Alembic from there:

```bash
cd src

# Generate a migration after changing models
alembic revision --autogenerate -m "describe change"

# Apply migrations
alembic upgrade head
```

Set `POSTGRES_URL` to target Postgres; otherwise Alembic falls back to the configured SQLite database.

In CD, `alembic upgrade head` runs inside the built image before traffic is switched, using `POSTGRES_URL` from GitHub Secrets.

## Deployment configuration

The CD pipeline expects these GitHub Secrets: `AZURE_CREDENTIALS`, `ACR_NAME`, `ACR_PASSWORD`, `RESOURCE_GROUP`, `ACI_NAME`, `ACR_IMAGE_NAME`, `SECRET_KEY`, `POSTGRES_URL`, `DATABASE_URL`, `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_STORAGE_CONTAINER`.

At runtime the container reads `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALGORITHM`, `POSTGRES_URL`, `DATABASE_URL`, `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_STORAGE_CONTAINER`, `QR_ASSETS_DIR` and `QR_TEMP_DIR`. Asset directories are created automatically at startup.

## Tooling

```bash
pip install pre-commit
pre-commit install
```

Hooks run ruff and black in check mode on commit. Line length is 88 for both (see `pyproject.toml`).

## License

MIT — see [LICENSE](LICENSE).
