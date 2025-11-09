#!/usr/bin/env pwsh
# PowerShell startup script for Product Distribution Backend

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("docker", "local", "dev")]
    [string]$Mode = "docker"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Product Distribution System - Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Start-Docker {
    Write-Host "Starting with Docker..." -ForegroundColor Green

    # Check if .env exists, if not copy from .env.example
    if (-not (Test-Path ".env")) {
        Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "Please review and update .env file with your settings" -ForegroundColor Yellow
    }

    # Check if Docker is running
    try {
        docker info | Out-Null
    }
    catch {
        Write-Host "Error: Docker is not running. Please start Docker and try again." -ForegroundColor Red
        exit 1
    }

    # Build and start containers
    Write-Host "Building and starting Docker containers..." -ForegroundColor Green
    docker-compose up --build -d

    Write-Host ""
    Write-Host "Containers started successfully!" -ForegroundColor Green
    Write-Host "API available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "To stop: docker-compose down" -ForegroundColor Yellow
}

function Start-Local {
    Write-Host "Starting locally..." -ForegroundColor Green

    # Check if Python is available
    try {
        python --version | Out-Null
    }
    catch {
        Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
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
    }

    # Start the application
    Write-Host ""
    Write-Host "Starting application..." -ForegroundColor Green
    Write-Host "API available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

function Start-Dev {
    Write-Host "Starting development mode with hot reload..." -ForegroundColor Green

    # Check if Python is available
    try {
        python --version | Out-Null
    }
    catch {
        Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
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
    }

    # Start with reload
    Write-Host ""
    Write-Host "Starting in development mode..." -ForegroundColor Green
    Write-Host "API available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Main execution
switch ($Mode) {
    "docker" { Start-Docker }
    "local" { Start-Local }
    "dev" { Start-Dev }
    default {
        Write-Host "Invalid mode. Use: docker, local, or dev" -ForegroundColor Red
        exit 1
    }
}
