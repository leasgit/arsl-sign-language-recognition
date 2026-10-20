$ErrorActionPreference = "Stop"

Write-Host "Building ArSL Sign Recognition for Windows..." -ForegroundColor Cyan

python -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --console `
  --name "ArSL Sign Recognition" `
  --add-data "arsl_cnn_model.keras;." `
  --add-data "hand_landmarker.task;." `
  --collect-all mediapipe `
  --hidden-import mediapipe.tasks.c `
  run_app.py

Write-Host "" 
Write-Host "Build complete." -ForegroundColor Green
Write-Host "Open: dist\ArSL Sign Recognition\ArSL Sign Recognition.exe"
