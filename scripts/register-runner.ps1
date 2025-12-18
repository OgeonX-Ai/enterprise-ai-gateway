[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GitHubToken,

    [string]$RepoOwner = "OgeonX-Ai",

    [string]$RepoName = "enterprise-ai-gateway",

    [string]$RunnerName = $env:COMPUTERNAME,

    [string]$RunnerLabels = "self-hosted,windows,docker,minikube",

    [string]$RunnerDir = "C:\\actions-runner",

    [string]$RunnerVersion = "2.317.0"
)

set-strictmode -version latest
$ErrorActionPreference = "Stop"

function Test-IsAdmin {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-RegistrationToken {
    param(
        [string]$Owner,
        [string]$Repo,
        [string]$Token
    )

    $headers = @{
        Authorization = "Bearer $Token"
        Accept        = "application/vnd.github+json"
    }

    $uri = "https://api.github.com/repos/$Owner/$Repo/actions/runners/registration-token"
    $response = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers

    if (-not $response.token) {
        throw "Failed to retrieve a registration token from GitHub."
    }

    return $response.token
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if (-not (Test-Path -Path $RunnerDir)) {
    Write-Host "Creating runner directory at $RunnerDir" -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $RunnerDir | Out-Null
}

Push-Location $RunnerDir
try {
    $configPath = Join-Path $RunnerDir "config.cmd"
    $zipPath = Join-Path $RunnerDir "actions-runner-win-x64-$RunnerVersion.zip"
    $downloadUrl = "https://github.com/actions/runner/releases/download/v$RunnerVersion/actions-runner-win-x64-$RunnerVersion.zip"

    if (-not (Test-Path -Path $configPath)) {
        Write-Host "Downloading GitHub Actions runner v$RunnerVersion..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath

        Write-Host "Extracting runner archive..." -ForegroundColor Cyan
        Expand-Archive -Path $zipPath -DestinationPath $RunnerDir -Force
        Remove-Item -Path $zipPath -Force
    }

    Write-Host "Requesting short-lived runner registration token..." -ForegroundColor Cyan
    $registrationToken = Get-RegistrationToken -Owner $RepoOwner -Repo $RepoName -Token $GitHubToken

    Write-Host "Configuring runner '$RunnerName' with labels: $RunnerLabels" -ForegroundColor Cyan
    & "$configPath" --url "https://github.com/$RepoOwner/$RepoName" --token $registrationToken --name $RunnerName --labels $RunnerLabels --unattended --replace

    if (-not (Test-IsAdmin)) {
        Write-Error "Service installation requires an elevated PowerShell session. Please rerun this script as Administrator to install and start the service."
        exit 1
    }

    Write-Host "Installing runner as a Windows service..." -ForegroundColor Cyan
    & .\svc install

    Write-Host "Starting runner service..." -ForegroundColor Cyan
    & .\svc start

    Write-Host "Runner registration complete. Verify the runner under Settings > Actions > Runners for the $RepoOwner/$RepoName repository." -ForegroundColor Green
} finally {
    Pop-Location
}
