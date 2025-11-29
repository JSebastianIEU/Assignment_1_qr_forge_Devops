# QR Forge

QR Forge is a FastAPI-powered web application for generating, customising, and managing QR codes locally. Users can sign up, preview designs, store personalised QR codes, download SVG/PNG assets, inspect history, and manage their profile information.

## Features
- **Authentication & profiles** – JWT-based signup/login, profile editing, and account deletion.
- **Rich QR generator** – live preview with colour, size, padding, border-radius controls, including transparent backgrounds.
- **Asset management** – save customised QR codes, download history entries (SVG/PNG), and export CSV summaries.
- **Responsive frontend** – HTML/CSS/JS experience aligned with the provided wireframes and diagrams.
- **Self-contained storage** – SQLite + SQLModel with per-user QR records; generated assets stored locally.

## Prerequisites
- Python **3.11+** installed and on your PATH
- Git (optional but recommended)
- PowerShell or a Unix-like shell (commands provided for both Windows and macOS/Linux)

## Getting started

### 1. Clone the repository
```bash
# HTTPS
git clone https://github.com/your-account/assignment_1_qr_forge_devops.git
cd assignment_1_qr_forge_devops
```

### 2. Create & activate a virtual environment
```bash
# Windows PowerShell
python -m venv .venv
. .venv\Scripts\Activate.ps1

# macOS / Linux (bash/zsh)
python -m venv .venv
source .venv/bin/activate
```
You should see `(.venv)` in your prompt. To exit later, run `deactivate`.

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. (Optional) Configure environment variables
Create a `.env` file (or export variables in your shell) to mirror production/Azure App Service:
```
# Auth / security
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=720
ALGORITHM=HS256

# Database
POSTGRES_URL=postgresql://<user>:<password>@<host>:5432/<db>  # optional; recommended for production
# Falls back to SQLite when POSTGRES_URL is unset
DATABASE_URL=sqlite:////home/data/qrcodes.db

# Asset directories
QR_ASSETS_DIR=/home/site/wwwroot/qr_assets
QR_TEMP_DIR=/home/site/wwwroot/qr_temp
```
Reasonable defaults are applied when not supplied; directories are created automatically at startup.

### 5. Run the application
```bash
uvicorn app:app --reload
```
- UI: http://127.0.0.1:8000/
- API docs (Swagger): http://127.0.0.1:8000/docs

Create an account via the UI or through the `/api/auth/signup` endpoint, then explore the generator, history, and profile sections.

### 6. Run the tests
```bash
pytest
```
The test-suite spins up an in-memory SQLite database and overrides the QR asset directories, so it never touches your local data files.

### 7. Build & run with Docker
```bash
docker build -t qr-app .
docker run -p 8000:8000 qr-app
```
- UI: http://127.0.0.1:8000/
- API docs: http://127.0.0.1:8000/docs

### 8. Useful maintenance commands
```bash
# format & lint (optional if you add tooling)
python -m ruff check .
python -m ruff format .

# clean generated assets
Remove-Item generated_svgs/* -Force
Remove-Item generated_pngs/* -Force
```

## CI pipeline
- GitHub Actions workflow (`.github/workflows/ci.yaml`) runs on every push (except `main`) and on PRs to `main`.
- Steps: checkout, set up Python 3.11, install deps, run `coverage run -m pytest` then `coverage report --fail-under=70`, and build the Docker image (`docker build -t qr-app-ci .`).
- Coverage gate: pipeline fails if coverage < 70%.

## Azure App Service configuration
Set the following application settings in the App Service (or in your deployment slot):
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ALGORITHM`
- `POSTGRES_URL` (e.g., `postgresql://<user>:<password>@<host>:5432/<db>`) for production
- `DATABASE_URL` (e.g., `sqlite:////home/data/qrcodes.db`) used when `POSTGRES_URL` is unset
- `QR_ASSETS_DIR` (e.g., `/home/site/wwwroot/qr_assets`)
- `QR_TEMP_DIR` (e.g., `/home/site/wwwroot/qr_temp`)
Directories for asset storage are auto-created at startup.

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

## Screenshots & diagrams
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
├── app.py                 # FastAPI entry point + route registration
├── config.py              # Environment configuration
├── core/                  # Auth/security helpers (password hashing, JWT)
├── db.py                  # SQLModel engine + session factory
├── models.py              # SQLModel tables (users, QR items)
├── routers/               # Modular API routers (auth, users, qr, export)
├── schemas.py             # Pydantic models / request & response schemas
├── services/              # QR rendering utilities (SVG/PNG generation)
├── static/                # CSS/JS/assets used by the UI
├── storage.py             # Reserved for future storage helpers (currently stub)
├── templates/             # HTML templates rendered by FastAPI
├── tests/                 # Pytest suite (uses in-memory DB fixtures)
├── assets/                # Shared icons used in the UI
├── generated_svgs/        # Runtime SVG assets (ignored by git)
├── generated_pngs/        # Runtime PNG assets (ignored by git)
├── report/                # Final report and annex diagrams/mockups
└── README.md
```

## Database migrations

This project uses Alembic to manage schema migrations for the SQLModel models.

- Local / developer workflow:
  1. Set `POSTGRES_URL` in your shell if you want to run migrations against Postgres (optional). Example (PowerShell):
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
  - The repository CD workflow runs `alembic upgrade head` during deployment. It expects a repository secret named `POSTGRES_URL` to be set (or `DATABASE_URL` used by the app). Ensure the secret contains a valid Postgres connection string for your production database.

Notes:
- For quick local work you can generate migration scripts using an SQLite URL (for example `sqlite:///alembic_tmp.db`) and commit the generated files. Apply them later against your production Postgres instance once connectivity is available.
- Remember to remove or tighten temporary firewall rules you created to allow your developer IP when finished (or prefer a private connectivity solution like Private Link or managed identities).

