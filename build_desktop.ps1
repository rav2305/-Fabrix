$ErrorActionPreference = "Stop"

py -3 -m pip install pyinstaller | Out-Null
py -3 -m PyInstaller --noconfirm --clean FabrixManager.spec

Write-Host "Desktop executable created at dist\\FabrixManager.exe"
