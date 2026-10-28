$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$launcher = Join-Path $PSScriptRoot 'dist\StudentExamPrediction\RUN_APP.ps1'
if (-not (Test-Path -LiteralPath $launcher)) {
    Write-Host 'Standalone app not built yet. Run BUILD_WINDOWS.bat first on a Windows PC with internet.' -ForegroundColor Yellow
    Read-Host 'Press Enter to exit'
    exit 1
}
& $launcher
