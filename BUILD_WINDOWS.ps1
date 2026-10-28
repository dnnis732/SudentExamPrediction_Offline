$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

Write-Host 'Python 3.14 standalone Windows builder' -ForegroundColor Cyan
Write-Host 'Build PC: Windows x64, Python 3.14 x64, and internet are required.'
Write-Host 'The target offline PC does not need Python installed.'
try {
    $versionOutput = & py -3.14 --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw 'Python 3.14 was not found. Install Python 3.14 x64 and the Python Launcher.'
    }
    Write-Host "Using $versionOutput"
} catch {
    Write-Host $_ -ForegroundColor Red
    Read-Host 'Press Enter to exit'
    exit 1
}

& cmd.exe /c "`"$PSScriptRoot\BUILD_WINDOWS.bat`""
if ($LASTEXITCODE -ne 0) {
    throw "Build failed. Review the errors shown above."
}
