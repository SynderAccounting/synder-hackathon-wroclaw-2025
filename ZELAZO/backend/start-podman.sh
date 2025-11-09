#!/bin/bash
# Bash Podman/Docker startup script for Product Distribution Backend

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
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "Product Distribution System - Backend"
echo "Podman/Docker Container Mode"
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
    echo "Please install Podman or Docker and try again."
    exit 1
fi

# Check if container engine is running
if ! $CONTAINER_TOOL info > /dev/null 2>&1; then
    echo "Error: $CONTAINER_TOOL is not running. Please start $CONTAINER_TOOL and try again."
    exit 1
fi

# Handle down command
if [ "$DOWN" = true ]; then
    echo "Stopping and removing containers..."
    $CONTAINER_TOOL compose down
    echo "Containers stopped and removed successfully!"
    exit 0
fi

# Handle logs command
if [ "$LOGS" = true ]; then
    echo "Showing container logs (Press Ctrl+C to exit)..."
    $CONTAINER_TOOL compose logs -f
    exit 0
fi

# Check if .env exists, if not copy from .env.example
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please review and update .env file with your settings"
    echo ""
fi

# Build and start containers
if [ "$BUILD" = true ]; then
    echo "Building and starting containers..."
    $CONTAINER_TOOL compose up --build -d
else
    echo "Starting containers..."
    $CONTAINER_TOOL compose up -d
fi

echo ""
echo "Containers started successfully!"
echo "========================================"
echo "API available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Useful commands:"
echo "  View logs:        ./start-podman.sh --logs"
echo "  Stop containers:  ./start-podman.sh --down"
echo "  Rebuild:          ./start-podman.sh --build"
echo ""
echo "Or use $CONTAINER_TOOL compose directly:"
echo "  $CONTAINER_TOOL compose logs -f"
echo "  $CONTAINER_TOOL compose ps"
echo "  $CONTAINER_TOOL compose down"
