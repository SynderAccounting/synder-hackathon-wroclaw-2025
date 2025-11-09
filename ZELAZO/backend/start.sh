#!/bin/bash
# Bash startup script for Product Distribution Backend

set -e

MODE="${1:-docker}"

echo "========================================"
echo "Product Distribution System - Backend"
echo "========================================"
echo ""

start_docker() {
    echo "Starting with Docker..."

    # Check if .env exists, if not copy from .env.example
    if [ ! -f ".env" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "Please review and update .env file with your settings"
    fi

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo "Error: Docker is not running. Please start Docker and try again."
        exit 1
    fi

    # Build and start containers
    echo "Building and starting Docker containers..."
    docker-compose up --build -d

    echo ""
    echo "Containers started successfully!"
    echo "API available at: http://localhost:8000"
    echo "API docs at: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
}

start_local() {
    echo "Starting locally..."

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is not installed or not in PATH."
        exit 1
    fi

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        echo "Virtual environment created successfully!"
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    if [ -f "venv/Scripts/activate" ]; then
        # Windows (Git Bash/MSYS)
        source venv/Scripts/activate
    elif [ -f "venv/bin/activate" ]; then
        # Linux/Mac
        source venv/bin/activate
    else
        echo "Error: Could not find activation script"
        exit 1
    fi

    # Always upgrade pip and install/update dependencies
    echo "Upgrading pip..."
    python -m pip install --upgrade pip --quiet

    echo "Installing/updating dependencies from requirements.txt..."
    pip install -r requirements.txt --upgrade --quiet
    echo "Dependencies installed successfully!"

    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "Please review and update .env file with your settings"
    fi

    # Start the application
    echo ""
    echo "Starting application..."
    echo "API available at: http://localhost:8000"
    echo "API docs at: http://localhost:8000/docs"
    echo ""
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

start_dev() {
    echo "Starting development mode with hot reload..."

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is not installed or not in PATH."
        exit 1
    fi

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        echo "Virtual environment created successfully!"
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    if [ -f "venv/Scripts/activate" ]; then
        # Windows (Git Bash/MSYS)
        source venv/Scripts/activate
    elif [ -f "venv/bin/activate" ]; then
        # Linux/Mac
        source venv/bin/activate
    else
        echo "Error: Could not find activation script"
        exit 1
    fi

    # Always upgrade pip and install/update dependencies
    echo "Upgrading pip..."
    python -m pip install --upgrade pip --quiet

    echo "Installing/updating dependencies from requirements.txt..."
    pip install -r requirements.txt --upgrade --quiet
    echo "Dependencies installed successfully!"

    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "Please review and update .env file with your settings"
    fi

    # Start with reload
    echo ""
    echo "Starting in development mode..."
    echo "API available at: http://localhost:8000"
    echo "API docs at: http://localhost:8000/docs"
    echo ""
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Main execution
case "$MODE" in
    docker)
        start_docker
        ;;
    local)
        start_local
        ;;
    dev)
        start_dev
        ;;
    *)
        echo "Invalid mode. Usage: $0 {docker|local|dev}"
        echo ""
        echo "Modes:"
        echo "  docker - Run with Docker Compose (default)"
        echo "  local  - Run locally with virtual environment"
        echo "  dev    - Run in development mode with hot reload"
        exit 1
        ;;
esac
