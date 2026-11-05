@echo off
cd /d "%~dp0"
if not exist "runtime\node.exe" (
  echo Run Start-Agent.cmd once to prepare the runtime.
  pause
  exit /b 1
)
pushd "sample-output\project"
"..\..\runtime\node.exe" "..\..\runtime\npm\bin\npm-cli.js" ci --ignore-scripts --no-audit --no-fund
if errorlevel 1 goto failed
echo Starting API: http://localhost:3000/health
"..\..\runtime\node.exe" server.js
popd
exit /b 0
:failed
popd
pause
exit /b 1
