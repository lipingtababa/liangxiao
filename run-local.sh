#!/bin/bash

# SyntheticCodingTeam Local Development Script
# This script starts the development environment with hot reloading

set -e

echo "🚀 Starting SyntheticCodingTeam Development Environment"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "📝 Please edit .env file with your configuration"
    else
        echo "❌ .env.example not found. Please create .env file manually."
        exit 1
    fi
fi

echo "🔨 Building development containers..."
docker-compose build

echo "🏃 Starting services with hot reloading..."
docker-compose up -d

echo "✅ Services started successfully!"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "📋 Available Commands:"
echo "  View logs:           docker-compose logs -f"
echo "  View poller logs:    docker-compose logs -f poller"
echo "  View agent logs:     docker-compose logs -f agent"
echo "  Stop services:       docker-compose down"
echo "  Restart services:    docker-compose restart"
echo ""
echo "🔗 Service URLs:"
echo "  Agent webhook:       http://localhost:3001"
echo ""
echo "💡 Development Features:"
echo "  ✅ Hot reloading enabled"
echo "  ✅ Source code mounted as volumes"
echo "  ✅ Development logging"
echo ""
echo "🔍 Monitoring GitHub issues assigned to 'lipingtababa'"
echo "   Repository: lipingtababa/liangxiao"
echo "   Poll interval: 30 seconds"