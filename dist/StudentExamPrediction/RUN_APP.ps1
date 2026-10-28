$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
Start-Process -FilePath (Join-Path $PSScriptRoot 'StudentExamPrediction.exe')
