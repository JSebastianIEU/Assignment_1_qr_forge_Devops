# Sprint 1 – Calidad de código, refactor y testing

## Refactors clave

- Configuración centralizada en `config.py` leyendo SECRET_KEY, expiración JWT, algoritmo, URL de BD y rutas de assets desde variables de entorno (`python-dotenv` cargado).
- `db.py` ahora expone `get_engine` con `init_db(engine)` opcional para facilitar el mock en tests; sin lógica de negocio en la capa de persistencia.
- Routers adelgazados: `routers/auth.py`, `routers/user.py` y `routers/qr.py` delegan la lógica a servicios (`services/auth.py`, `services/user.py`, `services/qr_items.py`) dejando sólo orquestación HTTP.
- Validaciones movidas a `schemas.py`: contraseñas con longitud mínima, título con límite, overlay_text con máximo 4 caracteres y patrones de color estrictos; modelos sin lógica de negocio.
- Servicios de QR separados por responsabilidad en `services/qr.py` (configuración, matriz, render, persistencia en disco) y `services/qr_items.py` (uso de DB + ownership + paths).

## Estrategia de testing y cobertura

- Tests unitarios nuevos para `core.security` (hash, verificación y JWT + usuario actual) y `services.qr` (render/encode/generación de assets con `tmp_path`).
- Validaciones de schemas (`tests/test_schemas.py`) cubren colores inválidos, URL inválida, texto demasiado largo y tamaños fuera de rango.
- Tests de integración con `TestClient`: flujo completo signup/login → preview → create → download SVG/PNG → delete, verificando registros en DB y archivos en los directorios temporales.
- Cobertura ejecutada con:
  - `& .\.venv\Scripts\python.exe -m coverage run -m pytest`
  - `& .\.venv\Scripts\python.exe -m coverage report --fail-under=70`
- Cobertura obtenida: **96%** (umbral ≥70% cumplido).
