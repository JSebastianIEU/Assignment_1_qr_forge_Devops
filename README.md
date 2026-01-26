# QR Forge (DevOps Assignment 1 - Part 2)

Badges: ![CI](https://img.shields.io/badge/ci-passing-brightgreen) ![coverage](https://img.shields.io/badge/coverage-0%25-red)

QR Forge is a FastAPI application for generating and managing QR codes. This second deliverable builds on Assignment 1 and focuses on DevOps hardening (tests, CI/CD, observability) while keeping the goal: a free, unlimited QR generator that anyone can use.

## Live endpoints
- Production app: https://jsebastianqrapp.azurewebsites.net
- Swagger docs: https://jsebastianqrapp.azurewebsites.net/docs
- Prometheus metrics: https://jsebastianqrapp.azurewebsites.net/metrics
- Health probe: https://jsebastianqrapp.azurewebsites.net/health

## Assignment context
- Assignment 1 (original build) lives in `Assignment1/`; this README documents the second part where DevOps automation, testing, and cloud deployment were added.
- Goal of the app stays the same: open, no-limit QR generation for all users (UI + API).

## What you will find
- Generator UI and API for creating branded QR codes (PNG or SVG) with color, padding, radius, and size controls.
- Authenticated history, profile, and download flows so users can revisit and export prior QRs.
- Tests (unit + integration) with a coverage gate (>=70%); local coverage sits around 92%.
- CI/CD to Azure: hardened multi-stage Docker image, migrations from the built image, staging smoke tests, and production swap.
- Monitoring via Prometheus `/metrics`, optional local Prom/Grafana stack, and structured logging.

## Page map (UI)
- `home.html`: landing hero that links to the generator and history.
- `index.html`: generator workspace with preview, download (SVG/PNG), and history drawer.
- `history.html`: saved QR list for the signed-in user.
- `profile.html`: update name/password or delete the account and owned QR codes.
- `login.html` / `signup.html`: entry points for authentication.

## Repo docs and references
- Deployment report: REPORT.md (Azure resources, CI/CD flow, validations).
- Annexed diagrams and wireframes: `report/annex/*` (flow, sequence, ERD, mockups).
- Monitoring assets: `monitoring/docker-compose.monitoring.yml` and `monitoring/grafana-dashboard.json`.

## Quick highlights (DevOps focus)
- Tests: unit + integration with enforced coverage gate (>=70%).
- CI: GitHub Actions runs ruff/black checks, tests, coverage, and builds a test Docker image.
- CD: Builds and pushes the multi-stage image to ACR, runs Alembic migrations inside the image, deploys to Azure Web App, and smoke-tests `/health`.
- Container: multi-stage Dockerfile, non-root `app` user, `HEALTHCHECK`, runtime image excludes dev/test tooling.
- Monitoring: Prometheus `/metrics` endpoint plus optional local Prometheus + Grafana stack.

## Key files (high-signal)
- `.github/workflows/ci.yaml` - CI with caching, lint/test/coverage gate, Trivy scan, and image build.
- `.github/workflows/cd.yaml` - build/push to ACR, run migrations from the image, deploy to Azure Web App, smoke-test.
- `Dockerfile` - multi-stage, non-root image with healthcheck and lean runtime stage.
- `app/main.py`, `app/config.py`, `app/db.py` - FastAPI app factory, settings, and SQLModel engine/session factory.
- `monitoring/` - Prometheus compose file and Grafana dashboard JSON.
- `frontend/` - React 18 + TypeScript + Tailwind SPA served by FastAPI (Vite build output copied to `app/static-frontend`).

## Prerequisites
- Python 3.11+ on PATH
- Git (recommended)
- PowerShell or a Unix-like shell

## Run locally
1) Clone
```bash
git clone https://github.com/your-account/assignment_1_qr_forge_devops.git
cd assignment_1_qr_forge_devops
```

2) Virtual environment
```bash
# Windows PowerShell
python -m venv .venv
. .venv\Scripts\Activate.ps1

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

3) Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4) Environment (optional but recommended)
Create `.env` (or export variables):
```
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=720
ALGORITHM=HS256

# Database (Postgres preferred in prod; SQLite fallback locally)
POSTGRES_URL=postgresql://<user>:<password>@<host>:5432/<db>
DATABASE_URL=sqlite:////home/app/data/qrcodes.db

# Asset dirs (auto-created)
QR_ASSETS_DIR=/home/app/data/qr_assets
QR_TEMP_DIR=/home/app/data/qr_temp
```

5) Run the app
```bash
uvicorn app.main:app --reload
```
- UI: http://127.0.0.1:8000/
- Docs: http://127.0.0.1:8000/docs
- Metrics: http://127.0.0.1:8000/metrics

Create an account via the UI or `/api/auth/signup`, then try the generator, history, and profile sections.

Frontend (React SPA)
```bash
cd frontend
npm install
npm run dev
```
- Vite server at http://localhost:3000 with `/api` proxied to `http://localhost:8000`.

6) Tests
```bash
pytest
```
Tests use an in-memory SQLite database and temp asset folders, so your local data is untouched.

7) Docker
```bash
docker build -t qr-app .
docker run -p 8000:8000 qr-app
```
- UI: http://127.0.0.1:8000/
- Docs: http://127.0.0.1:8000/docs

8) Useful maintenance commands
```bash
# lint/format (if installed)
python -m ruff check .
python -m ruff format .

# clean generated assets
Remove-Item generated_svgs/* -Force
Remove-Item generated_pngs/* -Force
```

## CI / CD overview
- CI (`.github/workflows/ci.yaml`): runs ruff + black (check), unit/integration tests, produces `coverage.xml` and `tests/results.xml`, enforces `--fail-under=70`, builds a test Docker image, and runs Trivy scan.
- CD (`.github/workflows/cd.yaml`): on `main` pushes or manual trigger; builds and pushes the image to Azure Container Registry, runs Alembic migrations inside the image with `POSTGRES_URL`, deploys to Azure Web App, and smoke-tests `/health`.
- Azure resources (from REPORT.md): ACR `jsebastianacr` and Web App `jsebastianqrapp` (Linux, Basic B1) pulling the image via managed identity.

## Monitoring and metrics
- `/metrics` exposes Prometheus-compatible counters and histograms (request count, latency, status codes).
- Local observability: `docker compose -f monitoring/docker-compose.monitoring.yml up` after starting the app.
  - Prometheus: http://localhost:9090
  - Grafana: http://localhost:3000 (admin/admin) using `monitoring/grafana-dashboard.json`.

## Logging
Structured logging is enabled. Set `LOG_LEVEL` (`DEBUG`, `INFO`, `WARNING`, `ERROR`) to adjust verbosity. Logs include timestamp, level, module, and message.

## Pre-commit and tooling
```powershell
pip install pre-commit
pre-commit install
```
Hooks run ruff and black (check mode) on commit.

## Azure App Service settings
Set in the Web App (or slot):
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ALGORITHM`
- `POSTGRES_URL` (e.g. `postgresql://<user>:<password>@<host>:5432/<db>`)
- `DATABASE_URL` (SQLite fallback)
- `QR_ASSETS_DIR` (e.g. `/home/app/data/qr_assets`)
- `QR_TEMP_DIR` (e.g. `/home/app/data/qr_temp`)
Asset directories are created automatically at startup.

## API overview
| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST | `/api/auth/signup` | Create a new user |
| POST | `/api/auth/login` | Obtain an access token |
| POST | `/api/auth/logout` | Invalidate current token (no server storage) |
| GET | `/api/user/me` | Current user profile |
| PATCH | `/api/user/me` | Update full name / password |
| DELETE | `/api/user/me` | Delete account and owned QR codes |
| POST | `/api/qr/preview` | Render a personalised QR preview |
| POST | `/api/qr` | Persist a QR configuration |
| GET | `/api/qr` / `/api/qr/history` | List the current user's QR items |
| DELETE | `/api/qr/{id}` | Remove a saved QR |
| GET | `/api/qr/{id}/download?format=svg|png` | Download saved assets |
| GET | `/api/export/csv` | Export history as CSV |

All protected routes require a bearer token (`Authorization: Bearer <token>`).

## Screenshots and diagrams
| Resource | Location |
| -------- | -------- |
| Home wireframe | `report/annex/wireframe-mockup/Home.png` |
| Generator wireframe | `report/annex/wireframe-mockup/Generator.png` |
| History wireframe | `report/annex/wireframe-mockup/History.png` |
| Login wireframe | `report/annex/wireframe-mockup/Login.png` |
| Profile wireframe | `report/annex/wireframe-mockup/Profile.png` |
| Flow diagram | `report/annex/Application Flow Diagram.pdf` |
| Sequence diagram | `report/annex/Application Architecture Sequence Diagram.pdf` |
| Data model (ERD) | `report/annex/Application Data Model (ERD).pdf` |

## Project structure
```
.
+-- app/                   # Application package
|   +-- main.py            # FastAPI app + route registration
|   +-- server.py          # ASGI entrypoint (uvicorn app.server:app)
|   +-- config.py          # Environment configuration
|   +-- db.py              # SQLModel engine + session factory
|   +-- models.py          # SQLModel tables (users, QR items)
|   +-- schemas.py         # Pydantic models / request & response schemas
|   +-- core/              # Auth/security helpers (password hashing, JWT)
|   +-- routers/           # Modular API routers (auth, users, qr, export)
|   +-- services/          # QR rendering utilities (SVG/PNG generation)
|   +-- monitoring/        # Metrics/observability helpers
|   +-- home/              # Static marketing pages
|   +-- static/            # CSS/JS/assets used in the UI
|   +-- assets/            # Shared icons used in the UI
|   +-- templates/         # HTML templates rendered by FastAPI
|   +-- generated_svgs/    # Runtime SVG assets (ignored by git)
|   +-- generated_pngs/    # Runtime PNG assets (ignored by git)
+-- alembic/               # Alembic migrations
+-- alembic.ini
+-- Dockerfile
+-- requirements.txt
+-- requirements-dev.txt
+-- tests/                 # Pytest suite (uses in-memory DB fixtures)
+-- logs/                  # Local logs (not needed in production)
+-- .github/workflows/     # CI/CD definitions
+-- report/                # Final report and annex diagrams/mockups
+-- README.md
```

## Database migrations
This project uses Alembic to manage schema migrations for the SQLModel models.

- Local workflow:
  1. Set `POSTGRES_URL` if running against Postgres (optional). Example (PowerShell):
     ```powershell
     $env:POSTGRES_URL = "postgresql://<user>:<password>@<host>:5432/<db>"
     ```
  2. Create and activate your virtualenv and install dependencies:
     ```bash
     python -m venv .venv
     source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
     python -m pip install -r requirements.txt
     ```
  3. Generate a migration (if you changed models):
     ```bash
     alembic revision --autogenerate -m "describe change"
     ```
  4. Apply migrations to the target database:
     ```bash
     alembic upgrade head
     ```

- CI/CD behavior:
  - The CD workflow runs `alembic upgrade head` during deployment using the built image. It expects `POSTGRES_URL` (or `DATABASE_URL`) to be configured as a secret.

Notes:
- For quick local work you can generate migration scripts using an SQLite URL (for example `sqlite:///alembic_tmp.db`) and commit the generated files. Apply them later against your production Postgres instance once connectivity is available.
- Remember to remove or tighten any temporary firewall rules after running migrations, or prefer managed identities/private connectivity where possible.
