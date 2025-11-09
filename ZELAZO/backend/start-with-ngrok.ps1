#!/usr/bin/env pwsh
# PowerShell startup script with ngrok public URL

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Product Distribution System - Backend" -ForegroundColor Cyan
Write-Host "Local Development with ngrok" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    python --version | Out-Null
}
catch {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# Check if ngrok is installed
if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "Error: ngrok is not installed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install ngrok:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://ngrok.com/download" -ForegroundColor White
    Write-Host "2. Or use: choco install ngrok (if you have Chocolatey)" -ForegroundColor White
    Write-Host "3. Or use: scoop install ngrok (if you have Scoop)" -ForegroundColor White
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Install/update dependencies
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip --quiet

Write-Host "Installing/updating dependencies..." -ForegroundColor Green
pip install -r requirements.txt --upgrade --quiet
Write-Host "Dependencies installed successfully!" -ForegroundColor Green

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

# Load environment variables
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*?)\s*$') {
            $name = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Check if ngrok token is set
if (-not $env:NGROK_AUTHTOKEN) {
    Write-Host "Error: NGROK_AUTHTOKEN is not set in .env file" -ForegroundColor Red
    Write-Host "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Yellow
    exit 1
}

# Configure ngrok
Write-Host ""
Write-Host "Configuring ngrok..." -ForegroundColor Green
ngrok config add-authtoken $env:NGROK_AUTHTOKEN 2>&1 | Out-Null

# Run database migrations
Write-Host ""
Write-Host "Running database migrations..." -ForegroundColor Green
try {
    $migrationOutput = python -m alembic upgrade head 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database migrations completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠ Warning: Migration encountered issues" -ForegroundColor Yellow
        Write-Host "Continuing with application startup..." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠ Warning: Could not run migrations" -ForegroundColor Yellow
    Write-Host "Continuing with application startup..." -ForegroundColor Yellow
}

# Start ngrok in background
Write-Host ""
Write-Host "Starting ngrok tunnel..." -ForegroundColor Green
$ngrokProcess = Start-Process -FilePath "ngrok" -ArgumentList "http", "--config=ngrok.yml", "8000" -PassThru -WindowStyle Minimized

# Wait a moment for ngrok to start
Start-Sleep -Seconds 3

# Get ngrok public URL
try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method Get
    $publicUrl = $ngrokApi.tunnels[0].public_url

    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✓ ngrok tunnel established!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Public URL:  $publicUrl" -ForegroundColor Green
    Write-Host "Local URL:   http://localhost:8000" -ForegroundColor White
    Write-Host "API Docs:    $publicUrl/docs" -ForegroundColor White
    Write-Host "ngrok Web:   http://localhost:4040" -ForegroundColor White
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Could not retrieve ngrok URL" -ForegroundColor Yellow
    Write-Host "Check ngrok dashboard at: http://localhost:4040" -ForegroundColor White
    Write-Host ""
}

# Start the application
Write-Host ""
Write-Host "Starting application..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server and ngrok" -ForegroundColor Yellow
Write-Host ""

# Cleanup function
$cleanup = {
    Write-Host ""
    Write-Host "Stopping ngrok..." -ForegroundColor Yellow
    Stop-Process -Id $ngrokProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Goodbye!" -ForegroundColor Cyan
}

# Register cleanup on exit
Register-EngineEvent PowerShell.Exiting -Action $cleanup | Out-Null

try {
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} finally {
    & $cleanup
}
