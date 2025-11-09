#!/bin/bash

# Docker Quick Start Script for Linux/Mac

COMMAND=${1:-dev}

echo -e "\033[0;36mSynderhacks Docker Manager\033[0m"
echo -e "\033[0;36m=========================\033[0m"
echo ""

case $COMMAND in
    dev)
        echo -e "\033[0;32mStarting in DEVELOPMENT mode...\033[0m"
        docker-compose -f docker-compose.dev.yml up --build
        ;;
    prod)
        echo -e "\033[0;32mStarting in PRODUCTION mode...\033[0m"
        docker-compose up -d --build
        echo ""
        echo -e "\033[0;32mServices started!\033[0m"
        echo -e "\033[0;33mFrontend: http://localhost:3000\033[0m"
        echo -e "\033[0;33mBackend: http://localhost:8000\033[0m"
        echo -e "\033[0;33mAPI Docs: http://localhost:8000/docs\033[0m"
        ;;
    down)
        echo -e "\033[0;33mStopping all services...\033[0m"
        docker-compose down
        echo -e "\033[0;32mServices stopped!\033[0m"
        ;;
    logs)
        echo -e "\033[0;33mShowing logs (Ctrl+C to exit)...\033[0m"
        docker-compose logs -f
        ;;
    clean)
        echo -e "\033[0;31mCleaning up Docker resources...\033[0m"
        docker-compose down -v --remove-orphans
        docker system prune -f
        echo -e "\033[0;32mCleanup complete!\033[0m"
        ;;
    rebuild)
        echo -e "\033[0;33mRebuilding without cache...\033[0m"
        docker-compose build --no-cache
        docker-compose up -d
        echo -e "\033[0;32mRebuild complete!\033[0m"
        ;;
    *)
        echo -e "\033[0;31mUnknown command: $COMMAND\033[0m"
        ;;
esac

echo ""
echo -e "\033[0;36mAvailable commands:\033[0m"
echo -e "\033[0;37m  ./docker.sh dev      - Start in development mode (hot-reload)\033[0m"
echo -e "\033[0;37m  ./docker.sh prod     - Start in production mode (optimized)\033[0m"
echo -e "\033[0;37m  ./docker.sh down     - Stop all services\033[0m"
echo -e "\033[0;37m  ./docker.sh logs     - View logs\033[0m"
echo -e "\033[0;37m  ./docker.sh clean    - Clean up resources\033[0m"
echo -e "\033[0;37m  ./docker.sh rebuild  - Rebuild without cache\033[0m"
