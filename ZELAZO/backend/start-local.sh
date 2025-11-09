#!/bin/bash
# Bash local startup script for Product Distribution Backend

set -e

echo "========================================"
echo "Product Distribution System - Backend"
echo "Local Development Mode"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.12+ and try again."
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
    echo ""
fi

# Run database migrations
echo ""
echo "Running database migrations..."
if python -m alembic upgrade head 2>&1; then
    echo "✓ Database migrations completed successfully!"
else
    echo "⚠ Warning: Migration encountered issues"
    echo "Continuing with application startup..."
fi

# Start the application
echo ""
echo "Starting application with hot reload..."
echo "========================================"
echo "API available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
