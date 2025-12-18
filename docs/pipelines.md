# Pipelines (Windows Self-Hosted Runner)

This repository includes a small set of GitHub Actions pipelines designed to run on a Windows-based self-hosted runner. They aim to provide a smoke test, practical Python CI, and an optional CD path into a local Minikube cluster.

## Workflows

### Runner Smoke Test
- **File:** [.github/workflows/runner-smoke.yml](../.github/workflows/runner-smoke.yml)
- **Purpose:** Quickly verify the Windows runner is healthy and that key tools (Docker, kubectl) are reachable.
- **Triggers:** `workflow_dispatch` or `push` when the workflow file changes.
- **What it does:** Prints user/machine/OS/PowerShell info, Git version, and probes Docker and kubectl without failing if they are missing.

### CI - Python Backend (System Python)
- **File:** [.github/workflows/ci-python.yml](../.github/workflows/ci-python.yml)
- **Purpose:** Lint and test the Python backend whether it lives in the repo root or under `backend/`.
- **Triggers:** `push` to `main` and any `pull_request`.
- **What it does:**
  - Checks out code and uses the system Python already installed on the Windows runner (install Python 3.11+ and ensure it is on `PATH`; 3.11–3.12 recommended because PyAV/faster-whisper wheels are not yet available for Python 3.13). No `actions/setup-python` step is required.
  - Installs dependencies from `backend/requirements.txt` if present, else `requirements.txt`.
  - Executes bundled helper scripts for consistency with local dev: `scripts/lint-check.ps1` (Ruff) and `scripts/test.ps1` (Pytest with skip-if-missing logic).
  - Test discovery looks for `test_*.py` or `*_test.py` and exits cleanly with a message when none are present.

### Showcase Summary
- **File:** [.github/workflows/showcase-summary.yml](../.github/workflows/showcase-summary.yml)
- **Purpose:** Produce a LinkedIn-friendly summary run that exercises lint/tests via the shared scripts and prints the runner/tool context for demos.
- **Triggers:** `workflow_dispatch` and `push` to `main` affecting README/docs or the workflow itself.
- **What it does:** Prints repo/run/runner metadata, shows key tool versions (Python, pip, Docker, Minikube, kubectl), runs `scripts/lint-check.ps1` and `scripts/test.ps1`, then outputs a short highlight list with doc pointers.

### CD - Minikube (Windows)
- **File:** [.github/workflows/cd-minikube.yml](../.github/workflows/cd-minikube.yml)
- **Purpose:** Optionally build and deploy the backend container image to a local Minikube cluster on the runner.
- **Triggers:** `workflow_dispatch` and `push` to `main` when `backend/**`, `k8s/**`, `Dockerfile`, or the workflow file change.
- **What it does:**
  - Verifies Docker is available; if not, it logs and exits successfully without running further steps.
  - Checks kubectl (best-effort), confirms Minikube is installed, and ensures it is running—starting it with the Docker driver if needed; failures skip the deployment without marking the workflow as failed.
  - Configures the Docker environment to point at Minikube, builds the `python-backend:latest` image using the root `Dockerfile` or `backend/Dockerfile` fallback, and ensures Kubernetes manifests exist (creating a minimal deployment/service if `k8s/` is missing) before applying them.
  - Waits for a rollout if a deployment name can be detected, and prints the `python-backend` service URL when available.

## Running the workflows

- **Smoke test:** Trigger the workflow manually in GitHub Actions (`Runner Smoke Test`) or push a change to `.github/workflows/runner-smoke.yml`.
- **CI:** Open a pull request or push to `main`; the `CI - Python Backend (System Python)` workflow will run automatically.
- **Showcase Summary:** Run `workflow_dispatch` for `Showcase Summary` or push relevant README/docs changes on `main`.
- **CD to Minikube:** Run `workflow_dispatch` for `CD - Minikube (Windows)` or push relevant changes on `main`. Ensure the runner has working Docker, Minikube (with Docker driver), and kubectl.

## Prerequisites for Minikube CD

- Docker installed and running on the Windows host.
- Minikube installed (`minikube start --driver=docker` should succeed).
- kubectl available (either installed globally or provided by Minikube).
- A `Dockerfile` at the repository root or under `backend/`. The workflow uses `python-backend:latest` as the image tag.
- Kubernetes manifests under `k8s/`. If missing, the workflow will write minimal deployment/service manifests before applying.

## Viewing logs and troubleshooting

- Open the workflow run in GitHub Actions and expand each step to see detailed PowerShell output.
- Look for messages such as "Skipping deployment" or "No tests found" to understand intentional skips.
- For Minikube issues, ensure Docker is running and that `minikube status` reports `Running`. Restart the Minikube VM with `minikube delete` and `minikube start --driver=docker` if necessary.
