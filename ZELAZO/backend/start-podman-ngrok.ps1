#!/usr/bin/env pwsh
# PowerShell Podman/Docker startup script with ngrok

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
Write-Host "Container Mode with ngrok" -ForegroundColor Cyan
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
    exit 1
}

# Check if container engine is running
try {
    & $containerTool info | Out-Null
}
catch {
    Write-Host "Error: $containerTool is not running." -ForegroundColor Red
    exit 1
}

# Handle down command
if ($Down) {
    Write-Host "Stopping and removing containers..." -ForegroundColor Yellow
    & $containerTool compose -f docker-compose-ngrok.yml down
    Write-Host "Containers stopped!" -ForegroundColor Green
    exit 0
}

# Handle logs command
if ($Logs) {
    Write-Host "Showing container logs (Press Ctrl+C to exit)..." -ForegroundColor Yellow
    & $containerTool compose -f docker-compose-ngrok.yml logs -f
    exit 0
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "IMPORTANT: Set your NGROK_AUTHTOKEN in .env file!" -ForegroundColor Yellow
    Write-Host "Get it from: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to continue after setting your token"
}

# Load and check NGROK_AUTHTOKEN
$envContent = Get-Content ".env"
$ngrokToken = ($envContent | Select-String "^NGROK_AUTHTOKEN=(.+)" | ForEach-Object { $_.Matches.Groups[1].Value })

if (-not $ngrokToken) {
    Write-Host "Error: NGROK_AUTHTOKEN is not set in .env file" -ForegroundColor Red
    Write-Host "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Yellow
    exit 1
}

# Build and start containers
if ($Build) {
    Write-Host "Building and starting containers with ngrok..." -ForegroundColor Green
    & $containerTool compose -f docker-compose-ngrok.yml up --build -d
} else {
    Write-Host "Starting containers with ngrok..." -ForegroundColor Green
    & $containerTool compose -f docker-compose-ngrok.yml up -d
}

# Wait for ngrok to be ready
Write-Host "Waiting for ngrok tunnel to establish..." -ForegroundColor Yellow

# Try multiple times to get the URL
$publicUrl = $null
$maxAttempts = 15
$attempt = 0

while ($attempt -lt $maxAttempts -and -not $publicUrl) {
    Start-Sleep -Seconds 2
    $attempt++

    try {
        $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method Get -ErrorAction SilentlyContinue
        if ($ngrokApi.tunnels -and $ngrokApi.tunnels.Count -gt 0) {
            $publicUrl = $ngrokApi.tunnels[0].public_url
        }
    } catch {
        # Silently continue
    }

    if (-not $publicUrl) {
        Write-Host "." -NoNewline
    }
}

Write-Host ""

if ($publicUrl) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✓ Containers started with ngrok!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Public URL:  $publicUrl" -ForegroundColor Green
    Write-Host "Local URL:   http://localhost:8000" -ForegroundColor White
    Write-Host "API Docs:    $publicUrl/docs" -ForegroundColor White
    Write-Host "ngrok Web:   http://localhost:4040" -ForegroundColor White
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "⚠ Could not retrieve ngrok URL automatically" -ForegroundColor Yellow
    Write-Host "ngrok might still be starting up." -ForegroundColor White
    Write-Host ""
    Write-Host "To get your URL:" -ForegroundColor Yellow
    Write-Host "1. Open: http://localhost:4040" -ForegroundColor White
    Write-Host "2. Or check container logs: $containerTool compose -f docker-compose-ngrok.yml logs ngrok" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs:        .\start-podman-ngrok.ps1 -Logs" -ForegroundColor White
Write-Host "  Stop containers:  .\start-podman-ngrok.ps1 -Down" -ForegroundColor White
Write-Host "  Rebuild:          .\start-podman-ngrok.ps1 -Build" -ForegroundColor White
