@echo off
setlocal
cd /d "%~dp0"

where node >nul 2>&1
if errorlevel 1 (
  echo Node.js was not found on PATH. Please install Node.js 20 LTS or newer.
  pause
  exit /b 1
)

where pnpm >nul 2>&1
if errorlevel 1 (
  for /f "delims=" %%i in ('npm prefix -g 2^>nul') do set "PATH=%PATH%;%%i"
)

where pnpm >nul 2>&1
if errorlevel 1 (
  echo pnpm was not found. Run: npm install -g pnpm
  pause
  exit /b 1
)

if not exist "node_modules" (
  echo Installing dependencies...
  call pnpm install
  if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
  )
)

echo ========================================
echo   Factory Simulator (Dev Server)
echo ========================================
echo Local Client:   http://localhost:5173
echo Local Server:   ws://localhost:2567
echo.
echo Network URLs (open from phone/other device on the same Wi-Fi/LAN):
powershell -NoProfile -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback|vEthernet|WSL|Docker|Virtual' -and $_.IPAddress -ne '127.0.0.1' -and $_.PrefixOrigin -ne 'WellKnown' } | Sort-Object { if ($_.InterfaceAlias -match 'Wi-Fi') { 0 } elseif ($_.InterfaceAlias -match 'Ethernet') { 1 } else { 2 } } | ForEach-Object { Write-Output ('  [' + $_.InterfaceAlias + '] http://' + $_.IPAddress + ':5173  (server ws://' + $_.IPAddress + ':2567)') }" 2>nul
echo.
echo Note: Allow Node.js / ports 5173 and 2567 in Windows Firewall if prompted.
echo Press Ctrl+C to stop.
echo ========================================
echo.

call pnpm dev

if errorlevel 1 (
  echo.
  echo Server exited with an error.
  pause
)
