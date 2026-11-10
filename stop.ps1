# ========================================================
# QueryMind - Stop Script
# Stops the Backend (port 8000) and Frontend (port 5173) services.
# ========================================================

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  Stopping QueryMind Services..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

function Stop-PortProcess([int]$port, [string]$name) {
    $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($connections) {
        $pidsToKill = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pidsToKill) {
            try {
                $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
                if ($proc) {
                    Write-Host "Stopping $name (PID: $procId - $($proc.Name))..." -ForegroundColor Cyan
                    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                }
            } catch {
                Write-Host "Could not stop PID $procId: $_" -ForegroundColor Red
            }
        }
        Write-Host "$name on port $port stopped." -ForegroundColor Green
    } else {
        Write-Host "No active $name service found listening on port $port." -ForegroundColor DarkGray
    }
}

# Stop Backend (Port 8000)
Stop-PortProcess -port 8000 -name "Backend API"

# Stop Frontend (Port 5173)
Stop-PortProcess -port 5173 -name "Frontend Vite"

Write-Host "`nAll QueryMind services have been stopped." -ForegroundColor Green

