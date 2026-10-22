$ErrorActionPreference = "Stop"

$compilerPaths = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)

$compiler = $compilerPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $compiler) {
    Write-Host "Inno Setup 6 was not found." -ForegroundColor Yellow
    Write-Host "Install Inno Setup, then run this script again."
    exit 1
}

if (-not (Test-Path "dist\ArSL Sign Recognition\ArSL Sign Recognition.exe")) {
    Write-Host "The packaged app was not found. Building it first..." -ForegroundColor Cyan
    & .\build_windows.ps1
}

Write-Host "Building Windows installer..." -ForegroundColor Cyan
& $compiler "installer.iss"

Write-Host ""
Write-Host "Installer complete." -ForegroundColor Green
Write-Host "Open: installer_output\ArSL_Sign_Recognition_Setup.exe"
