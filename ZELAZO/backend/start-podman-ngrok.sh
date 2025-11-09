#!/bin/bash
# Bash Podman/Docker startup script with ngrok

set -e

# Parse arguments
DOWN=false
LOGS=false
BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --down|-d)
            DOWN=true
            shift
            ;;
        --logs|-l)
            LOGS=true
            shift
            ;;
        --build|-b)
            BUILD=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --down, -d     Stop and remove containers"
            echo "  --logs, -l     Show container logs"
            echo "  --build, -b    Build containers before starting"
            echo "  --help, -h     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "Product Distribution System - Backend"
echo "Container Mode with ngrok"
echo "========================================"
echo ""

# Check if podman or docker is available
CONTAINER_TOOL=""
if command -v podman &> /dev/null; then
    CONTAINER_TOOL="podman"
    echo "Using Podman"
elif command -v docker &> /dev/null; then
    CONTAINER_TOOL="docker"
    echo "Using Docker"
else
    echo "Error: Neither Podman nor Docker is installed."
    exit 1
fi

# Check if container engine is running
if ! $CONTAINER_TOOL info > /dev/null 2>&1; then
    echo "Error: $CONTAINER_TOOL is not running."
    exit 1
fi

# Handle down command
if [ "$DOWN" = true ]; then
    echo "Stopping and removing containers..."
    $CONTAINER_TOOL compose -f docker-compose-ngrok.yml down
    echo "Containers stopped!"
    exit 0
fi

# Handle logs command
if [ "$LOGS" = true ]; then
    echo "Showing container logs (Press Ctrl+C to exit)..."
    $CONTAINER_TOOL compose -f docker-compose-ngrok.yml logs -f
    exit 0
fi

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

# Load and check NGROK_AUTHTOKEN
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$NGROK_AUTHTOKEN" ]; then
    echo "Error: NGROK_AUTHTOKEN is not set in .env file"
    echo "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

# Build and start containers
if [ "$BUILD" = true ]; then
    echo "Building and starting containers with ngrok..."
    $CONTAINER_TOOL compose -f docker-compose-ngrok.yml up --build -d
else
    echo "Starting containers with ngrok..."
    $CONTAINER_TOOL compose -f docker-compose-ngrok.yml up -d
fi

# Wait for ngrok to be ready
echo "Waiting for ngrok tunnel to establish..."

# Try multiple times to get the URL
PUBLIC_URL=""
MAX_ATTEMPTS=15
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ] && [ -z "$PUBLIC_URL" ]; do
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))

    # Try to get URL with better error handling
    PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | \
        grep -o '"public_url":"https://[^"]*"' | \
        head -1 | \
        cut -d'"' -f4 || echo "")

    if [ -z "$PUBLIC_URL" ]; then
        echo -n "."
    fi
done

echo ""

if [ ! -z "$PUBLIC_URL" ]; then
    echo ""
    echo "========================================"
    echo "✓ Containers started with ngrok!"
    echo "========================================"
    echo ""
    echo "Public URL:  $PUBLIC_URL"
    echo "Local URL:   http://localhost:8000"
    echo "API Docs:    $PUBLIC_URL/docs"
    echo "ngrok Web:   http://localhost:4040"
    echo ""
    echo "========================================"
else
    echo ""
    echo "⚠ Could not retrieve ngrok URL automatically"
    echo "ngrok might still be starting up."
    echo ""
    echo "To get your URL:"
    echo "1. Open: http://localhost:4040"
    echo "2. Or run: curl -s http://localhost:4040/api/tunnels | grep public_url"
    echo ""
fi

echo ""
echo "Useful commands:"
echo "  View logs:        ./start-podman-ngrok.sh --logs"
echo "  Stop containers:  ./start-podman-ngrok.sh --down"
echo "  Rebuild:          ./start-podman-ngrok.sh --build"
