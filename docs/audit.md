# Repository audit

## Components discovered
- **Backend (FastAPI)** in `backend/app`: runtime orchestration, provider registry, connectors (mock + Azure-aligned), API routes, settings, and middleware.
- **Frontend** in `web/`: static HTML/JS client that calls the gateway; no build tooling required.
- **Docs** in `docs/`: conceptual write-ups for architecture, connectors, security, observability, deployment, and routing.
- **Demo assets** in `demo/`: screenshots and notes for showcasing the experience.

## How components connect
- The FastAPI app creates a single `AgentRuntime` with in-memory `MemoryStore`, `ServiceRegistry`, policy engine, and router.
- API routes (`app/api/`) delegate to the shared runtime instance stored on `app.state`.
- Connectors implement async interfaces for LLM, RAG, speech, and service-desk services; mock connectors are the default so local runs avoid external dependencies.
- The static web client posts directly to the FastAPI endpoints; no reverse proxy or separate frontend server is required.

## Gaps identified for reliable dev/CI
- **Automated testing**: No pytest suite or integration coverage existed for the backend endpoints (now added under `backend/tests`).
- **Tooling**: No linting or single entrypoint for checks (addressed via `ruff` and `make check`).
- **CI/CD**: No GitHub Actions workflow to enforce tests on pull requests (added in `.github/workflows/ci.yml`).
- **Environment handling**: `.env.example` existed but README lacked quickstart/setup guidance (expanded in README plus docs). Secrets remain environment-driven; no in-repo secrets found.
- **Documentation**: Architecture/API docs were present but incomplete for onboarding; added new quickstart, architecture diagrams, API examples, contributing guide, and mockups.
