# Automated Failure Triage

This repository captures a lightweight triage artifact on job failure and uses Google Gemini to open a GitHub Issue with ready-to-use remediation guidance.

## How it works
- On any failing job in the smoke, CI, or Minikube CD workflows, a `_triage/summary.txt` file is written with run metadata and best-effort diagnostic versions.
- The summary is uploaded as an artifact named **triage**.
- The `Automated Failure Triage (Gemini)` workflow listens for failed runs of those workflows, downloads the artifact, redacts obvious secrets, and asks Gemini for a structured incident analysis.
- A new issue is created (if one is not already open for the same workflow + SHA) with:
  - Run URL, branch, and SHA
  - Collapsible triage notes
  - Gemini analysis with a “Codex Fix Prompt” block for fast handoff

## Configuring Gemini access
1. In the GitHub repository settings, add a secret `GEMINI_API_KEY` containing your Google AI Studio API key.
2. (Optional) Override the model by setting the workflow variable `GEMINI_MODEL` (default: `gemini-1.5-flash`).
3. The workflow never logs the secret and redacts common token patterns before calling Gemini.

## Issue creation and deduplication
- Issues are labeled `ci-failure` and `needs-codex-fix`.
- Before creating a new issue, the workflow searches open issues for the same workflow name and short SHA. If found, no new issue is opened.

## Using the “Codex Fix Prompt”
- The Gemini output includes a dedicated code block intended for Codex or another agent to apply fixes quickly.
- Copy the block into your agent to generate a patch; the triage notes and run URL provide additional context if needed.

## Security notes
- Redaction is best-effort. Avoid printing secrets in workflow logs or application output.
- The triage artifact only includes environment metadata and tool versions; it does not automatically upload full logs.

## Troubleshooting
- If no triage artifact is found, the workflow still opens an issue with basic run metadata.
- If Gemini is unavailable (network/quota), the issue will include a fallback message and the redacted triage notes.
