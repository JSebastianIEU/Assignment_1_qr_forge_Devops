# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]
- Add CI (coverage gate, Trivy) and CD (staging slot, swap, migrations)
- Convert Dockerfile to multi-stage, non-root user, HEALTHCHECK
- Health endpoint checks DB connectivity and returns 503 on failure
- Add monitoring configs (Prometheus/Grafana)
- Add tests: DB failure health, Alembic env import
- Improve `db.py` with pooling and sslmode enforcement
