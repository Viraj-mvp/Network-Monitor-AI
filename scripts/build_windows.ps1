#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build script for Network AI Monitor on Windows
.DESCRIPTION
    Creates a standalone executable using PyInstaller
#>

param(
    [switch]$Clean,
    [switch]$OneFile,
    [switch]$Install
)

$APP_NAME = "NetworkAIMonitor"
$ErrorActionPreference = "Stop"

function Write-Step($message) {
    Write-Host "`n=== $message ===" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "✓ $message" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "✗ $message" -ForegroundColor Red
}

# Print banner
Write-Host @"
╔══════════════════════════════════════════════════════════╗
║        Network AI Monitor - Windows Build Script         ║
╚══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Blue

# Clean if requested
if ($Clean) {
    Write-Step "Cleaning build directories"
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    Write-Success "Cleaned previous builds"
}

# Install dependencies if requested
if ($Install) {
    Write-Step "Installing dependencies"
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-build.txt
    Write-Success "Dependencies installed"
}

# Build
Write-Step "Building executable"
try {
    pyinstaller build/pyinstaller/NetworkMonitor.spec
    Write-Success "Build completed"
}
catch {
    Write-Error "Build failed: $_"
    exit 1
}

# Rename output
Write-Step "Preparing distribution"
if (Test-Path "dist\$APP_NAME") {
    Rename-Item "dist\$APP_NAME" "dist\$APP_NAME-Windows" -Force
    
    # Create ZIP
    Compress-Archive -Path "dist\$APP_NAME-Windows" -DestinationPath "dist\$APP_NAME-Windows.zip" -Force
    Write-Success "Created NetworkAIMonitor-Windows.zip"
}

# Summary
Write-Host "`n══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "  BUILD COMPLETE" -ForegroundColor Green
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "`nOutput:"
if (Test-Path "dist\$APP_NAME-Windows.zip") {
    $size = (Get-Item "dist\$APP_NAME-Windows.zip").Length / 1MB
    Write-Host "  • $APP_NAME-Windows.zip ($([math]::Round($size, 2)) MB)" -ForegroundColor White
}
Write-Host "`nTo test:"
Write-Host "  1. Extract dist\$APP_NAME-Windows.zip"
Write-Host "  2. Run $APP_NAME-Windows\$APP_NAME.exe"
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Blue
