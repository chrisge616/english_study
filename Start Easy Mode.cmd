@echo off
setlocal EnableExtensions

title Easy Mode Launcher

set "DISTRO=Ubuntu"
set "WSL_REPO=/home/chris/code/english_study"
set "WSL_PY=.venv/bin/python"
set "PORT=8000"
set "PS_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

pushd "%~dp0" >nul 2>nul
if errorlevel 1 (
  echo Easy Mode could not start because it could not switch to the launcher folder.
  echo.
  pause
  exit /b 1
)

where wsl.exe >nul 2>nul
if errorlevel 1 (
  echo Easy Mode could not start because WSL is not installed or not available on this Windows system.
  echo.
  pause
  exit /b 1
)

wsl -d "%DISTRO%" -e sh -lc "exit 0" >nul 2>nul
if errorlevel 1 (
  echo Easy Mode could not start because the WSL distro "%DISTRO%" was not found.
  echo.
  echo Install or restore the Ubuntu distro, then try again.
  echo.
  pause
  exit /b 1
)

wsl -d %DISTRO% --cd %WSL_REPO% sh -lc "test -d ."
if errorlevel 1 (
  echo Easy Mode could not start because the canonical repo path was not found:
  echo %WSL_REPO%
  echo.
  pause
  exit /b 1
)

wsl -d %DISTRO% --cd %WSL_REPO% sh -lc "test -d .venv"
if errorlevel 1 (
  echo Easy Mode could not start because the project virtual environment is missing.
  echo.
  echo Expected folder: %WSL_REPO%/.venv
  echo.
  pause
  exit /b 1
)

wsl -d %DISTRO% --cd %WSL_REPO% sh -lc "test -x %WSL_PY%"
if errorlevel 1 (
  echo Easy Mode could not start because Python inside the project virtual environment was not found.
  echo.
  echo Expected file: %WSL_REPO%/%WSL_PY%
  echo.
  pause
  exit /b 1
)

set "WSL_IP="
for /f "usebackq delims=" %%I in (`wsl -d %DISTRO% --cd %WSL_REPO% sh -lc "hostname -I | cut -d ' ' -f1" 2^>nul`) do if not defined WSL_IP set "WSL_IP=%%I"
if not defined WSL_IP (
  echo Easy Mode could not start because it could not determine the current WSL network address.
  echo.
  pause
  exit /b 1
)
set "URL=http://%WSL_IP%:%PORT%"

wsl -d %DISTRO% --cd %WSL_REPO% sh -lc "%WSL_PY% -c \"import socket,sys; s=socket.socket(); rc=s.connect_ex(('127.0.0.1', %PORT%)); s.close(); sys.exit(1 if rc == 0 else 0)\""
if errorlevel 1 (
  echo Easy Mode could not start because port %PORT% is already in use.
  echo.
  echo Close the other service using %URL% and try again.
  echo.
  pause
  exit /b 1
)

start "Easy Mode" wsl -d %DISTRO% --cd %WSL_REPO% sh -lc "%WSL_PY% -m app.easy_mode"
if errorlevel 1 (
  echo Easy Mode could not start the WSL server process.
  echo.
  pause
  exit /b 1
)

for /L %%I in (1,1,20) do (
  timeout /t 1 /nobreak >nul
  "%PS_EXE%" -NoProfile -Command "try { $null = Invoke-WebRequest -UseBasicParsing -Uri '%URL%' -TimeoutSec 1; exit 0 } catch { exit 1 }"
  if not errorlevel 1 goto open_browser
)

echo Easy Mode started, but the local UI did not respond in time.
echo.
echo Check the WSL window for an immediate startup error, then try again.
echo.
pause
exit /b 1

:open_browser
start "" "%URL%"
exit /b 0
