$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv-desktop\Scripts\python.exe"
if (-not (Test-Path $python)) {
    py -3.9 -m venv .venv-desktop
    if ($LASTEXITCODE -ne 0) { throw "Python 3.9 is required to build OnPazar." }
}

& $python -m pip install --no-cache-dir --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Could not prepare pip." }
& $python -m pip install --no-cache-dir -r requirements-desktop.txt
if ($LASTEXITCODE -ne 0) { throw "Could not install desktop build dependencies." }

$env:USERPROFILE = $PSScriptRoot
& $python -m PyInstaller --noconfirm --clean --windowed --onefile `
    --name OnPazar `
    --icon static\onpazar-favicon.ico `
    --add-data "templates;templates" `
    --add-data "static;static" `
    --add-data "data;data" `
    --collect-all webview `
    --collect-all pythonnet `
    --collect-all clr_loader `
    desktop_launcher.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed to build OnPazar.exe." }

$destination = Join-Path (Split-Path $PSScriptRoot -Parent) "OnPazar.exe"
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "dist\OnPazar.exe") -Destination $destination -Force
Write-Host "Built OnPazar desktop app: $destination"




