$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot "backend"
$venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    $systemPython = Join-Path $env:LocalAppData "Programs\Python\Python311\python.exe"

    if (-not (Test-Path $systemPython)) {
        throw "Python 3.11 was not found. Install Python and rerun this script."
    }

    & $systemPython -m venv (Join-Path $backendDir ".venv")
    & $venvPython -m pip install --cache-dir (Join-Path $backendDir ".pip-cache") -r (Join-Path $backendDir "requirements.txt")
}

Push-Location $backendDir

try {
    & $venvPython -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
}
finally {
    Pop-Location
}
