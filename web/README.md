# Web (static frontend)

A single-page HTML client that calls the local FastAPI backend. It lists available connectors and lets you send a message for routing.

## Usage

1. Start the backend: `uvicorn app.main:app --app-dir backend/app --reload`.
2. Open `web/index.html` directly in your browser.
3. Choose a connector, type a message, and view the response payload plus conversation memory.

## GitHub Pages

The `/web` folder is ready to be published via GitHub Pages. The page targets `http://localhost:8000` by default; adjust `API_BASE` in `index.html` to point to a deployed backend.
