param(
    [string]$Url = "http://127.0.0.1:8000/health"
)

$ErrorActionPreference = "Stop"
$response = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 10
if ($response.status -ne "ok") {
    throw "Unexpected health response from $Url"
}
Write-Output "OCTAVIO backend is healthy at $Url"
