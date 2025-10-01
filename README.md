# QR Forge

QR Forge is a FastAPI-powered web application for generating, customising, and managing QR codes locally. Users can sign up, preview designs, store personalised QR codes, download SVG/PNG assets, inspect history, and manage their profile information.

## Features
- **Authentication & profiles** – JSON Web Token-based signup/login, profile editing, and account deletion.
- **Rich QR generator** – live preview with colour, size, padding, and border-radius controls, including transparent backgrounds.
- **Asset management** – save customised QR codes, download history entries in SVG/PNG, and export CSV summaries.
- **Responsive frontend** – HTML/CSS/JS experience aligned with provided wireframes and diagrams.
- **Self-contained storage** – SQLite + SQLModel with per-user QR records, generated assets stored locally.

## Tech stack
- Python 3.11+
- FastAPI, SQLModel, SQLite, qrcode, Pillow
- HTML, CSS, Vanilla JS
- Pytest for API tests

## Getting started

### 1. Clone & install
```bash
python -m venv .venv
. .venv/Scripts/activate        # Windows PowerShell
pip install -r requirements.txt
```

### 2. Run the application
```bash
uvicorn app:app --reload
```
Visit http://127.0.0.1:8000/ for the UI or http://127.0.0.1:8000/docs for Swagger.

### 3. Run the tests
```bash
pytest
```
The test-suite spins up an in-memory SQLite database so it never touches your local data files.

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
| GET | `/api/qr/history` | List the current user's QR items |
| DELETE | `/api/qr/{id}` | Remove a saved QR |
| GET | `/api/qr/{id}/download` | Download SVG or PNG |
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

For quick manual verification, capture screenshots from the running app and place them in `docs/screenshots/` (optional) to keep them versioned alongside the diagrams.

## Project structure
```
.
├── app.py               # FastAPI entry point
├── routers/             # Modular API routers
├── services/            # QR rendering helpers
├── templates/           # HTML views
├── static/              # CSS/JS/assets
├── report/annex/        # Provided diagrams and mockups
└── tests/               # Pytest suite (in-memory DB)
```

## Contributing / next steps
- Ensure `pytest` is green before committing.
- Generated assets (`generated_svgs/`, `generated_pngs/`) are ignored by git; use the history drawer to inspect them locally.
- Future enhancements: richer profile editing, bulk history actions, additional QR formats.
