# Enterprise AI Gateway

Vendor-agnostic enterprise AI gateway for routing agents, LLMs, STT/TTS, and service desk integrations through a single control plane.

## Overview

This repository provides a portfolio-ready scaffold for an enterprise AI control plane. The demo pairs a static frontend with a locally running FastAPI backend so you can showcase routing, connector registration, and memory handoffs without relying on cloud services.

**How to describe it:**
- The frontend is hosted statically.
- The backend runs locally to simulate an enterprise AI control plane and service orchestration layer.

## Repository structure

- `docs/`: Architecture notes, routing behavior, security posture, and roadmap.
- `backend/`: FastAPI application that mocks connector registration, routing, and short-term memory.
- `web/`: Static HTML to invoke the backend and view responses.
- `demo/`: Quickstart for running the local demo and storing screenshots.

## Quickstart

1. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. **Run the backend**
   ```bash
   uvicorn app.main:app --app-dir backend/app --reload
   ```

3. **Open the frontend**
   Open `web/index.html` in your browser and submit a message. The page calls `http://localhost:8000` by default.

## Next steps

- Extend connectors with real vendor SDKs.
- Add authentication and role-based routing rules.
- Deploy the backend to your preferred cloud and point the static site at the new endpoint.

## License

MIT
