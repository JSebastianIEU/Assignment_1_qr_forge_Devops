# Sprint 1-2 – Calidad de código, refactor, testing y CI

## Refactors clave (Sprint 1)
- Config centralizada en `config.py` leyendo SECRET_KEY, expiración JWT, algoritmo, URL de BD y rutas de assets desde variables de entorno (`python-dotenv` cargado).
- `db.py` ahora expone `get_engine` con `init_db(engine)` opcional para facilitar mocks en tests; sin lógica de negocio en la capa de persistencia.
- Routers adelgazados: `routers/auth.py`, `routers/user.py` y `routers/qr.py` delegan la lógica a servicios (`services/auth.py`, `services/user.py`, `services/qr_items.py`) dejando solo orquestación HTTP.
- Validaciones movidas a `schemas.py`: contraseñas con longitud mínima, límite de título, overlay_text máx 4 caracteres y patrones de color estrictos; modelos sin lógica de negocio.
- Servicios de QR separados por responsabilidad en `services/qr.py` (configuración, matriz, render, persistencia en disco) y `services/qr_items.py` (uso de DB + ownership + paths).

## Estrategia de testing y cobertura
- Tests unitarios para `core.security` (hash, verificación y JWT + usuario actual) y `services.qr` (render/encode/generación de assets con `tmp_path`).
- Validaciones de schemas (`tests/test_schemas.py`) cubren colores inválidos, URL inválida, texto demasiado largo y tamaños fuera de rango.
- Tests de integración con `TestClient`: flujo completo signup/login → preview → create → download SVG/PNG → delete, verificando registros en DB y archivos en los directorios temporales.
- Cobertura ejecutada con:
  - `& .\.venv\Scripts\python.exe -m coverage run -m pytest`
  - `& .\.venv\Scripts\python.exe -m coverage report --fail-under=70`
- Cobertura obtenida: **96%** (umbral ≥70% cumplido).

## CI/CD base (Sprint 2)
- **Dockerfile**: imagen basada en `python:3.11-slim`, instala `requirements.txt`, copia el código y expone la app con `uvicorn app:app --host 0.0.0.0 --port 8000`.
- **Workflow CI** (`.github/workflows/ci.yaml`): se ejecuta en pushes (excepto `main`) y PRs hacia `main`. Pasos: checkout → setup Python 3.11 → instalar dependencias → `coverage run -m pytest` + `coverage report --fail-under=70` → `docker build -t qr-app-ci .`.
- **Cobertura mínima**: la acción falla si la cobertura es <70%.
- **Secrets preparados para CD**: crear en GitHub Actions los secrets `AZURE_CREDENTIALS` (JSON completo del SP) y opcionalmente `AZURE_APP_ID`, `AZURE_TENANT`, `AZURE_SP_PASSWORD` para habilitar `azure/login@v2` en el siguiente sprint.

## Enhancements added (Monitoring, Logging, CI/CD safety)

- **Logging**: structured logging added via `core/logging.py`. The app now configures logging at startup and uses `LOG_LEVEL` env var.
- **Metrics**: Prometheus instrumentation added using `prometheus_fastapi_instrumentator` (exposes `/metrics`). A `monitoring/` folder contains sample `prometheus.yml` and `docker-compose.monitoring.yml` for local testing.
- **CI**: lint step (ruff + black check) added; CI now generates `coverage.xml` and `tests/results.xml` artifacts uploaded to GitHub Actions.
- **CD**: migrations now run inside the built Docker image (`docker run --rm ... alembic upgrade head`) so the migrations use same code and dependencies as the deployed container; the workflow validates `POSTGRES_URL` secret before running migrations.

These changes specifically address the rubric items: code quality (linting), testing (artifact + coverage gate), CI/CD safety (migrations from image), monitoring (metrics + example configs) and observability (structured logs).
