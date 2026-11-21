$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendPath ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    python -m venv (Join-Path $backendPath ".venv")
}

& $venvPython -m pip install -r (Join-Path $backendPath "requirements-dev.txt")

$envExample = Join-Path $repoRoot ".env.example"
$localEnv = Join-Path $backendPath ".env"
if (-not (Test-Path $localEnv)) {
    Copy-Item $envExample $localEnv
    Write-Output "Created backend/.env with the local development token."
}
else {
    Write-Output "Kept existing backend/.env."
}
