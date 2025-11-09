#!/bin/bash
# Bash startup script with ngrok public URL

set -e

echo "========================================"
echo "Product Distribution System - Backend"
echo "Local Development with ngrok"
echo "========================================"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping ngrok..."
    if [ ! -z "$NGROK_PID" ]; then
        kill $NGROK_PID 2>/dev/null || true
    fi
    echo "Goodbye!"
    exit 0
}

# Register cleanup on exit
trap cleanup INT TERM EXIT

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    exit 1
fi

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "Error: ngrok is not installed."
    echo ""
    echo "Install ngrok:"
    echo "1. Download from: https://ngrok.com/download"
    echo "2. Or use: brew install ngrok/ngrok/ngrok (macOS)"
    echo "3. Or use: snap install ngrok (Linux)"
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
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Could not find activation script"
    exit 1
fi

# Install/update dependencies
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet

echo "Installing/updating dependencies..."
pip install -r requirements.txt --upgrade --quiet
echo "Dependencies installed successfully!"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Set your NGROK_AUTHTOKEN in .env file!"
    echo "Get it from: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo ""
    read -p "Press Enter to continue after setting your token..."
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if ngrok token is set
if [ -z "$NGROK_AUTHTOKEN" ]; then
    echo "Error: NGROK_AUTHTOKEN is not set in .env file"
    echo "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

# Configure ngrok
echo ""
echo "Configuring ngrok..."
ngrok config add-authtoken $NGROK_AUTHTOKEN >/dev/null 2>&1

# Run database migrations
echo ""
echo "Running database migrations..."
if python -m alembic upgrade head 2>&1; then
    echo "✓ Database migrations completed successfully!"
else
    echo "⚠ Warning: Migration encountered issues"
    echo "Continuing with application startup..."
fi

# Start ngrok in background
echo ""
echo "Starting ngrok tunnel..."
ngrok http --config=ngrok.yml 8000 > /dev/null 2>&1 &
NGROK_PID=$!

# Wait for ngrok to start
sleep 3

# Get ngrok public URL
PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null || echo "")

if [ ! -z "$PUBLIC_URL" ]; then
    echo "========================================"
    echo "✓ ngrok tunnel established!"
    echo "========================================"
    echo ""
    echo "Public URL:  $PUBLIC_URL"
    echo "Local URL:   http://localhost:8000"
    echo "API Docs:    $PUBLIC_URL/docs"
    echo "ngrok Web:   http://localhost:4040"
    echo ""
    echo "========================================"
else
    echo "⚠ Could not retrieve ngrok URL"
    echo "Check ngrok dashboard at: http://localhost:4040"
    echo ""
fi

# Start the application
echo ""
echo "Starting application..."
echo "Press Ctrl+C to stop the server and ngrok"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
