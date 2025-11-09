#!/usr/bin/env pwsh
# PowerShell Podman/Docker startup script for Product Distribution Backend

param(
    [Parameter(Mandatory=$false)]
    [switch]$Down,
    [Parameter(Mandatory=$false)]
    [switch]$Logs,
    [Parameter(Mandatory=$false)]
    [switch]$Build
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Product Distribution System - Backend" -ForegroundColor Cyan
Write-Host "Podman/Docker Container Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if podman or docker is available
$containerTool = $null
if (Get-Command podman -ErrorAction SilentlyContinue) {
    $containerTool = "podman"
    Write-Host "Using Podman" -ForegroundColor Green
} elseif (Get-Command docker -ErrorAction SilentlyContinue) {
    $containerTool = "docker"
    Write-Host "Using Docker" -ForegroundColor Green
} else {
    Write-Host "Error: Neither Podman nor Docker is installed." -ForegroundColor Red
    Write-Host "Please install Podman or Docker and try again." -ForegroundColor Yellow
    exit 1
}

# Check if container engine is running
try {
    & $containerTool info | Out-Null
}
catch {
    Write-Host "Error: $containerTool is not running. Please start $containerTool and try again." -ForegroundColor Red
    exit 1
}

# Handle down command
if ($Down) {
    Write-Host "Stopping and removing containers..." -ForegroundColor Yellow
    & $containerTool compose down
    Write-Host "Containers stopped and removed successfully!" -ForegroundColor Green
    exit 0
}

# Handle logs command
if ($Logs) {
    Write-Host "Showing container logs (Press Ctrl+C to exit)..." -ForegroundColor Yellow
    & $containerTool compose logs -f
    exit 0
}

# Check if .env exists, if not copy from .env.example
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please review and update .env file with your settings" -ForegroundColor Yellow
    Write-Host ""
}

# Build and start containers
if ($Build) {
    Write-Host "Building and starting containers..." -ForegroundColor Green
    & $containerTool compose up --build -d
} else {
    Write-Host "Starting containers..." -ForegroundColor Green
    & $containerTool compose up -d
}

Write-Host ""
Write-Host "Containers started successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs:        .\start-podman.ps1 -Logs" -ForegroundColor White
Write-Host "  Stop containers:  .\start-podman.ps1 -Down" -ForegroundColor White
Write-Host "  Rebuild:          .\start-podman.ps1 -Build" -ForegroundColor White
Write-Host ""
Write-Host "Or use $containerTool compose directly:" -ForegroundColor Yellow
Write-Host "  $containerTool compose logs -f" -ForegroundColor White
Write-Host "  $containerTool compose ps" -ForegroundColor White
Write-Host "  $containerTool compose down" -ForegroundColor White
