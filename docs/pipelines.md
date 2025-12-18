# Pipelines (Windows Self-Hosted Runner)

This repository includes a small set of GitHub Actions pipelines designed to run on a Windows-based self-hosted runner. They aim to provide a smoke test, practical Python CI, and an optional CD path into a local Minikube cluster.

## Workflows

### Runner Smoke (Windows)
- **File:** [.github/workflows/runner-smoke.yml](../.github/workflows/runner-smoke.yml)
- **Purpose:** Quickly verify the Windows runner is healthy and that key tools (Docker, kubectl) are reachable.
- **Triggers:** `workflow_dispatch` or `push` when the workflow file changes.
- **What it does:** Prints user/machine/OS/PowerShell info, Git version, and probes Docker and kubectl without failing if they are missing.

### CI - Python (Windows)
- **File:** [.github/workflows/ci-python.yml](../.github/workflows/ci-python.yml)
- **Purpose:** Lint and test the Python backend whether it lives in the repo root or under `backend/`.
- **Triggers:** `push` to `main` and any `pull_request`.
- **What it does:**
  - Checks out code and uses the system Python already installed on the Windows runner (install Python 3.11+ and ensure it is on `PATH`). No `actions/setup-python` step is required.
  - Installs dependencies from `backend/requirements.txt` if present, else `requirements.txt`, then always installs Ruff and Pytest.
  - Runs Ruff against `backend/` if it exists, otherwise the repository root.
  - Runs Pytest against `backend/` if it exists, otherwise the repository root. If no tests matching `test_*.py` or `*_test.py` are found, the job logs a friendly skip message and succeeds.

### CD - Minikube (Windows)
- **File:** [.github/workflows/cd-minikube.yml](../.github/workflows/cd-minikube.yml)
- **Purpose:** Optionally build and deploy the backend container image to a local Minikube cluster on the runner.
- **Triggers:** `workflow_dispatch` and `push` to `main` when `backend/**`, `k8s/**`, `Dockerfile`, or the workflow file change.
- **What it does:**
  - Verifies Docker is available; if not, it logs and exits successfully without running further steps.
  - Checks kubectl (best-effort) and ensures Minikube is running, attempting to start it with the Docker driver if needed; failures skip the deployment without marking the workflow as failed.
  - Configures the Docker environment to point at Minikube, builds the `python-backend:latest` image using the root `Dockerfile` or `backend/Dockerfile` fallback, and applies manifests from `k8s/`.
  - Waits for a rollout if a deployment name can be detected, and prints the `python-backend` service URL when available.

## Running the workflows

- **Smoke test:** Trigger the workflow manually in GitHub Actions (`Runner Smoke (Windows)`) or push a change to `.github/workflows/runner-smoke.yml`.
- **CI:** Open a pull request or push to `main`; the `CI - Python (Windows)` workflow will run automatically.
- **CD to Minikube:** Run `workflow_dispatch` for `CD - Minikube (Windows)` or push relevant changes on `main`. Ensure the runner has working Docker, Minikube (with Docker driver), and kubectl.

## Prerequisites for Minikube CD

- Docker installed and running on the Windows host.
- Minikube installed (`minikube start --driver=docker` should succeed).
- kubectl available (either installed globally or provided by Minikube).
- A `Dockerfile` at the repository root or under `backend/`. The workflow uses `python-backend:latest` as the image tag.
- Kubernetes manifests under `k8s/`. If missing, the workflow will skip deployment; this repo ships a basic `python-backend` deployment and NodePort service as defaults.

## Viewing logs and troubleshooting

- Open the workflow run in GitHub Actions and expand each step to see detailed PowerShell output.
- Look for messages such as "Skipping deployment" or "No tests found" to understand intentional skips.
- For Minikube issues, ensure Docker is running and that `minikube status` reports `Running`. Restart the Minikube VM with `minikube delete` and `minikube start --driver=docker` if necessary.
