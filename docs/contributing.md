# Contributing

## Branching and PRs
- Create feature branches from `main` (e.g., `feature/<short-description>`).
- Keep commits small and focused; prefer conventional messages (e.g., `test: add chat API coverage`).
- Open a Pull Request early and update it as you iterate. Include links to related issues.

## Coding standards
- Python style is enforced with `ruff` (error-level rules and import order). Run `make lint` before pushing.
- Keep FastAPI routes thin: validation and orchestration go through `AgentRuntime`.
- Prefer dependency injection via FastAPI request state over singletons for testability.
- Avoid adding new secrets to the repo; rely on environment variables defined in `.env.example`.

## Test checklist
- Add or update pytest coverage for new logic. Include both success and negative-path cases for new endpoints.
- Use the mock connectors for deterministic behavior; mock external SDK calls when adding new providers.
- Ensure `make check` passes locally before opening a PR.

## Review checklist
- API docs (`docs/api.md`) and README examples updated if signatures change.
- Architecture diagrams kept in sync when adding new components.
- Screenshots or mockups refreshed if the UI flow changes.
