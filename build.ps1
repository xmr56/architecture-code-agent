$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
python bootstrap_runtime.py
if ($LASTEXITCODE -ne 0) { throw 'Runtime setup failed' }
python -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'Build dependencies failed' }
python -m PyInstaller --noconfirm --onefile --windowed --name CodeAgent --add-data 'examples;examples' --add-binary 'runtime/node.exe;runtime' --add-data 'runtime/npm;runtime/npm' --add-data 'runtime/NODE-LICENSE.txt;runtime' app.py
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
Write-Host 'Executable: dist/CodeAgent.exe'
