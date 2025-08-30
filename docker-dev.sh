#!/bin/bash
# Docker development helper script

set -e

case "$1" in
    "build")
        echo "Building development image..."
        docker-compose build orchestrator
        ;;
    "up")
        echo "Starting development environment..."
        docker-compose up -d
        echo "Orchestrator available at http://localhost:8000"
        echo "API docs at http://localhost:8000/docs"
        echo "Logs: docker-compose logs -f orchestrator"
        ;;
    "down")
        echo "Stopping development environment..."
        docker-compose down
        ;;
    "logs")
        docker-compose logs -f orchestrator
        ;;
    "shell")
        docker-compose exec orchestrator bash
        ;;
    "test")
        echo "Running tests in container..."
        docker-compose exec orchestrator pytest tests/ -v
        ;;
    "format")
        echo "Formatting code..."
        docker-compose exec orchestrator black .
        docker-compose exec orchestrator isort .
        ;;
    "install")
        echo "Installing dependencies..."
        docker-compose exec orchestrator poetry install
        ;;
    "reset")
        echo "Resetting development environment..."
        docker-compose down -v
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    *)
        echo "Usage: $0 {build|up|down|logs|shell|test|format|install|reset}"
        echo ""
        echo "Commands:"
        echo "  build   - Build the development Docker image"
        echo "  up      - Start the development environment"
        echo "  down    - Stop the development environment"
        echo "  logs    - Follow application logs"
        echo "  shell   - Open shell in container"
        echo "  test    - Run tests"
        echo "  format  - Format code with black and isort"
        echo "  install - Install/update dependencies"
        echo "  reset   - Reset environment (rebuild and restart)"
        exit 1
        ;;
esac