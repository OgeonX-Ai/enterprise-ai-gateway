[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GitHubToken,

    [string]$RepoOwner = "OgeonX-Ai",

    [string]$RepoName = "enterprise-ai-gateway",

    [string]$RunnerDir = "C:\\actions-runner"
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
    throw "Runner directory '$RunnerDir' was not found. Nothing to unregister."
}

Push-Location $RunnerDir
try {
    $configPath = Join-Path $RunnerDir "config.cmd"

    Write-Host "Requesting short-lived runner deregistration token..." -ForegroundColor Cyan
    $registrationToken = Get-RegistrationToken -Owner $RepoOwner -Repo $RepoName -Token $GitHubToken

    if (Test-Path -Path (Join-Path $RunnerDir "svc.exe")) {
        if (-not (Test-IsAdmin)) {
            Write-Error "Service removal requires an elevated PowerShell session. Please rerun this script as Administrator to stop and remove the service."
            exit 1
        }

        Write-Host "Stopping runner service if running..." -ForegroundColor Cyan
        & .\svc stop

        Write-Host "Uninstalling runner service..." -ForegroundColor Cyan
        & .\svc uninstall
    }

    if (Test-Path -Path $configPath) {
        Write-Host "Removing runner registration..." -ForegroundColor Cyan
        & "$configPath" remove --unattended --token $registrationToken
    } else {
        Write-Warning "config.cmd not found in $RunnerDir. Skipping runner removal step."
    }

    Write-Host "Runner unregistration complete." -ForegroundColor Green
} finally {
    Pop-Location
}
