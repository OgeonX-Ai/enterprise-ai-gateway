# Self-hosted GitHub Actions runner (Windows)

This guide explains how to provision a Windows self-hosted GitHub Actions runner for the `OgeonX-Ai/enterprise-ai-gateway` repository without manually copying runner tokens from the UI. The included PowerShell scripts obtain short-lived registration tokens directly from the GitHub REST API and install the runner as a Windows service.

## Prerequisites
- Windows host with PowerShell 5.1+ or PowerShell 7+
- Local administrator rights (required to install/start the service)
- Outbound internet access to `github.com` to download the runner and call the GitHub API
- GitHub personal access token (PAT) with permissions to administer repository actions runners (e.g., **repo** scope for this repository)

## Security considerations
- The PAT is only used in memory to request a short-lived runner registration token; it is never written to disk by the scripts.
- Run the scripts from a trusted, elevated PowerShell session on the machine that will host the runner.
- Remove the runner when decommissioning the host to prevent orphaned agents.

## Quickstart: register the runner
1. Open an **elevated** PowerShell session on the Windows host.
2. Execute the registration script with your PAT:
   ```powershell
   .\scripts\register-runner.ps1 -GitHubToken "<YOUR_PAT>"
   ```
   Optional parameters allow overriding the repository, runner name, labels, installation directory (`C:\actions-runner` by default), and runner version (default `2.317.0`).
3. The script will download the runner if needed, request a registration token through the GitHub API, configure the runner with labels `self-hosted,windows,docker,minikube`, and install/start the service.

## Verify the runner in GitHub
- Navigate to **Settings > Actions > Runners** for `OgeonX-Ai/enterprise-ai-gateway`.
- The runner should appear with the configured name and labels and show as **Idle** when ready.

## Unregister and remove the runner
1. Open an **elevated** PowerShell session on the host.
2. Run the unregister script with the same repository context:
   ```powershell
   .\scripts\unregister-runner.ps1 -GitHubToken "<YOUR_PAT>"
   ```
3. The script will fetch a new token, stop and uninstall the service, and remove the runner registration.

## Example workflow usage
Use the configured labels to target this runner in your workflows:
```yaml
jobs:
  build:
    runs-on: [self-hosted, windows, docker, minikube]
    steps:
      - uses: actions/checkout@v4
      - name: Run build
        run: npm run build
```
