# Design Reflection

## Flow diagram alignment
- **Authentication guard** – Every generator/profile/history action runs behind FastAPI dependencies that require a bearer token, matching the decision branches in the application flow PDF.
- **Preview → Save sequence** – The UI enforces the preview-before-save loop shown in the mockups; previews hit `/api/qr/preview` and only persist when the user explicitly clicks “Save to history”.
- **History actions** – Download/delete buttons refresh the drawer and grid immediately, mirroring the “Manage Saved QR” branch of the flow.

## Sequence diagram alignment
- **Router layering** – `app.py` delegates to routers (`auth`, `user`, `qr`, `export`) that orchestrate database sessions and QR rendering services exactly like the sequence diagram’s “Controller → Service → DB” transitions.
- **Service isolation** – QR asset creation lives in `services/qr.py`, returning deterministic SVG/PNG strings so both preview and persistence share the same rendering step, matching the reusable service call in the diagram.
- **Response handling** – Swagger models (`QRPreviewResponse`, `QRItem`) surface the same payload fields that the diagram lists as responses back to the client.

## Data model (ERD) alignment
- **Entities** – `models.py` implements the `users` and `qr_items` tables with the same attributes (email, hashed_password, timestamps, QR metadata) defined in the ERD.
- **Relationships** – `QRItem.user_id` references `users.id` with a foreign key and indexed column, ensuring per-user history queries scale.
- **Defaults & constraints** – Colour defaults (`#000000`, `#FFFFFF`) and timestamp factories honour the ERD notes; password hashing and unique email checks prevent duplicates.

## Implementation notes
- Validation uses Pydantic schemas to reject empty URLs, malformed hex colours, and too-short passwords when updating profiles.
- Tests exercise authentication, preview, CRUD, and account lifecycle scenarios using the same in-memory database setup described in the plan.
- Swagger docs expose every route with request/response models, so the interactive API explorer mirrors the diagrams and README tables.
