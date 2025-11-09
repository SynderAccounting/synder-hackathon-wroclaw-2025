#!/usr/bin/env pwsh
# PowerShell local startup script for Product Distribution Backend

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Product Distribution System - Backend" -ForegroundColor Cyan
Write-Host "Local Development Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    python --version | Out-Null
}
catch {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.12+ and try again." -ForegroundColor Yellow
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

# Always upgrade pip and install/update dependencies
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip --quiet

Write-Host "Installing/updating dependencies from requirements.txt..." -ForegroundColor Green
pip install -r requirements.txt --upgrade --quiet
Write-Host "Dependencies installed successfully!" -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please review and update .env file with your settings" -ForegroundColor Yellow
    Write-Host ""
}

# Run database migrations
Write-Host ""
Write-Host "Running database migrations..." -ForegroundColor Green
try {
    $migrationOutput = python -m alembic upgrade head 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database migrations completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠ Warning: Migration encountered issues" -ForegroundColor Yellow
        Write-Host $migrationOutput -ForegroundColor Gray
        Write-Host "Continuing with application startup..." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠ Warning: Could not run migrations" -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Gray
    Write-Host "Continuing with application startup..." -ForegroundColor Yellow
}

# Start the application
Write-Host ""
Write-Host "Starting application with hot reload..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
