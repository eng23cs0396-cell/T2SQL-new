# ========================================================
# QueryMind - Start Script
# Starts FastAPI backend (port 8000) and Vite frontend (port 5173)
# and opens the web application in your default browser.
# ========================================================

$ErrorActionPreference = "Continue"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Set-Location $projectRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting QueryMind Text-to-SQL Platform" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Start Backend if not already running
$backendConn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $backendConn) {
    Write-Host "[1/3] Starting Backend API (Uvicorn on port 8000)..." -ForegroundColor Yellow
    $pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $pythonExe)) {
        $pythonExe = "python"
    }
    
    $backendProcess = Start-Process -FilePath $pythonExe `
        -ArgumentList "-m uvicorn backend.main:app --host 127.0.0.1 --port 8000" `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden `
        -PassThru
    
    Write-Host "      Backend started with PID $($backendProcess.Id)" -ForegroundColor DarkGray
} else {
    Write-Host "[1/3] Backend already running on http://127.0.0.1:8000" -ForegroundColor Green
}

# 2. Start Frontend if not already running
$frontendConn = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
if (-not $frontendConn) {
    Write-Host "[2/3] Starting Frontend (Vite on port 5173)..." -ForegroundColor Yellow
    $frontendDir = Join-Path $projectRoot "frontend"
    
    $frontendProcess = Start-Process -FilePath "npm.cmd" `
        -ArgumentList "run dev" `
        -WorkingDirectory $frontendDir `
        -WindowStyle Hidden `
        -PassThru
    
    Write-Host "      Frontend started with PID $($frontendProcess.Id)" -ForegroundColor DarkGray
} else {
    Write-Host "[2/3] Frontend already running on http://localhost:5173" -ForegroundColor Green
}

# 3. Wait for services to be available
Write-Host "[3/3] Verifying services readiness..." -ForegroundColor Yellow
$maxAttempts = 15
$attempt = 0
$ready = $false

while ($attempt -lt $maxAttempts -and -not $ready) {
    Start-Sleep -Seconds 1
    $attempt++
    $fConn = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
    $bConn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
    if ($fConn -and $bConn) {
        $ready = $true
    }
}

if ($ready) {
    Write-Host "`nAll services are LIVE!" -ForegroundColor Green
    Write-Host "  - Frontend UI:  http://localhost:5173" -ForegroundColor Cyan
    Write-Host "  - Backend Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
} else {
    Write-Host "`nWarning: Services are starting up, but ports took longer to report." -ForegroundColor Yellow
}

# 4. Open in browser
Write-Host "`nOpening http://localhost:5173 in your default browser..." -ForegroundColor Green
Start-Process "http://localhost:5173"

