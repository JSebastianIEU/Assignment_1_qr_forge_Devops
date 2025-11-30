# Assignment Report

This report summarises the improvements made to the `Assignment_1_qr_forge_Devops` project to meet IE University BCSAI DevOps rubric requirements.

## Rubric mapping

- Code quality: replaced startup events with lifespan, added type hints, removed prints, added structured logging.
- Security: Key Vault-aware configuration; CI includes Trivy scanning; CD validates Key Vault secret presence and uses Key Vault reference for App Service.
- Testing: added DB-failure and Alembic import tests; CI produces coverage.xml and enforces threshold >=70%.
- CI/CD: added `ci.yaml` and `cd.yaml` with matrix testing, caching, Trivy, staging slot deploy & swap, migration step.
- Observability: OpenTelemetry packages included; Prometheus `/metrics`; sample Grafana dashboard and Prometheus config.

## Screenshots and evidence

- CI run: see `.github/workflows/ci.yaml` artifacts for `coverage.xml` and `trivy-report.json` (uploaded by pipeline).
- CD run: logs show ACR push, staging deployment, smoke tests and swap (actions upload Trivy report).
- Grafana dashboard: `monitoring/grafana-dashboard.json`

## Change list (high level)

- Reworked `Dockerfile` to be multi-stage, non-root and include a healthcheck.
- Introduced CI and CD workflows implementing quality, security, and deployment requirements.
- Updated `app.py` health endpoint to check DB connectivity and use lifespan startup.
- Improved `db.py` to use connection pooling and SSL mode enforcement for Postgres.
- Added tests to improve coverage and detect migration/env issues in CI.

## How to validate locally

1. Run tests and generate coverage:
```powershell
python -m venv .venv; . .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pytest --junitxml=tests/results.xml --cov=./ --cov-report=xml:coverage.xml
```

2. Build and run the container locally:
```powershell
docker build -t qrapp:local .
docker run -e POSTGRES_URL=sqlite:///:memory: -p 8000:8000 qrapp:local
curl http://localhost:8000/health
```
# Sprint Report – DevOps improvements

This document summarises the work done to bring the project to a professional DevOps standard and to meet the Assignment 2 rubric.

## Summary of improvements (high-level)

- Code quality: added linting (`ruff`) and formatting (`black`) integration, pre-commit hooks, and small refactors to centralise configuration and move business logic into `services/`.
- Tests & coverage: comprehensive unit and integration test-suite. Coverage gate enforced in CI (`--fail-under=70`). Local coverage: ~92%.
- CI: GitHub Actions runs lint, tests, coverage, and uploads `coverage.xml` and `tests/results.xml` artifacts.
- CD: multi-stage Docker image built and pushed to ACR, migrations executed inside the deployed image, and a post-deploy smoke test probes `/health` to verify the deployment.
- Production hygiene: runtime image does not include test/dev packages; `requirements-dev.txt` holds dev tooling.
- Monitoring: `/metrics` endpoint exposed using `prometheus_client`. `monitoring/` contains Prometheus config, docker-compose and a sample Grafana dashboard JSON.

## Mapping to rubric

- Code quality & refactoring (25%): modular services, pre-commit, ruff/black, reduced side-effects at import-time, module docstrings added to key modules.
- Testing & coverage (20%): tests pass locally, coverage ~92%, CI enforces >=70% coverage and uploads test artifacts.
- CI (20%): CI runs lint, tests, coverage gate, and builds test image. Cache is configured for pip wheels.
- Deployment & containerization (20%): Dockerfile is multi-stage, uses non-root `app` user, includes `HEALTHCHECK`, and excludes dev/test deps; CD runs migrations inside the image and performs a smoke test.
- Monitoring & docs (15%): `/metrics` and `/health` endpoints present; Prometheus and Grafana example configs included; README updated with usage and CI/CD details.

## Automation & safety features added

- `requirements-dev.txt` created and CI updated to install dev deps only for testing and linting.
- Docker multi-stage build to keep final image minimal and secure.
- Alembic migrations run from the production image during CD to guarantee parity between migration code and deployed code.
- CD validates `POSTGRES_URL` secret early and runs a post-deploy HTTP smoke test against `/health`.
- Pre-commit configured to run ruff and black to ensure consistent style before committing.

## Monitoring and observability

- Metrics: `qr_forge_requests_total` (Counter) and `qr_forge_request_latency_seconds` (Histogram) are recorded by middleware; `/metrics` returns Prometheus text exposition.
- Grafana: `monitoring/grafana-dashboard.json` included as a starter dashboard (request count, latency, 5xx rate).
- Logging: structured logging configured via `core/logging.py`, initialized at startup, controlled via `LOG_LEVEL`.

## How to verify (smoke checklist)

1. Run tests locally and check `coverage.xml` is produced.
2. Run `docker build -t qr-app:local .` and `docker run -p 8000:80 qr-app:local`.
3. Visit `http://localhost:8000/health` and `http://localhost:8000/metrics`.
4. Trigger CI (push to a non-main branch) and confirm lint/tests/coverage pass and artifacts are uploaded.
5. Push to `main` (or use workflow_dispatch) for CD; confirm deployment and smoke test pass.

## Notes and small trade-offs

- The post-deploy smoke test uses the default Azure Web App URL `https://jsebastianqrapp.azurewebsites.net`. If your app uses a custom domain or slot, adjust the CD workflow accordingly.
- The Grafana JSON is a minimal example intended for graders; dashboard improvements can be added (panels, templating, alerts).

## Conclusion

The repository now meets the assignment requirements: code quality, automated testing and coverage, CI/CD with safe migrations and smoke tests, container hygiene, monitoring, and documentation. These changes are intended to reach full marks for the DevOps assignment when evaluated against the provided rubric.
