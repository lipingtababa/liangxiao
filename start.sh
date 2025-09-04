#!/bin/bash

# SyntheticCodingTeam Quick Start Script
# This script provides easy ways to start the SCT service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
MODE="local"
PORT=8000
ENV_FILE=".env"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            MODE="docker"
            shift
            ;;
        --docker-compose)
            MODE="docker-compose"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --env)
            ENV_FILE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --docker         Start with Docker"
            echo "  --docker-compose Start with Docker Compose"
            echo "  --port PORT      Port to run on (default: 8000)"
            echo "  --env FILE       Environment file (default: .env)"
            echo "  --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Start locally"
            echo "  $0 --docker           # Start with Docker"
            echo "  $0 --docker-compose   # Start with Docker Compose"
            echo "  $0 --port 8001        # Start on port 8001"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}�� SyntheticCodingTeam Startup${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Check for .env file
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: $ENV_FILE not found${NC}"
    echo "Please create a .env file with required credentials"
    echo ""
    echo "Required variables:"
    echo "  GITHUB_PERSONAL_ACCESS_TOKEN=..."
    echo "  OPENAI_API_KEY=..."
    echo "  GITHUB_WEBHOOK_SECRET=..."
    exit 1
fi

echo -e "${GREEN}✅ Loading environment from $ENV_FILE${NC}"

# Function to check if service is ready
check_service() {
    local url="http://localhost:$1/health"
    local max_attempts=30
    local attempt=0
    
    echo "⏳ Waiting for service at $url..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Service is ready!${NC}"
            return 0
        fi
        
        attempt=$((attempt + 1))
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "   Still waiting... (${attempt}s)"
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Service failed to start${NC}"
    return 1
}

# Start based on mode
case $MODE in
    docker-compose)
        echo "🐳 Starting with Docker Compose..."
        
        # Stop any existing containers
        docker-compose down 2>/dev/null || true
        
        # Start services
        docker-compose up -d
        
        if check_service $PORT; then
            echo ""
            echo -e "${GREEN}🎉 SCT is running with Docker Compose!${NC}"
            echo ""
            echo "📊 Services:"
            echo "  - API:      http://localhost:$PORT"
            echo "  - Docs:     http://localhost:$PORT/docs"
            echo "  - Health:   http://localhost:$PORT/health"
            echo "  - Debug:    http://localhost:$PORT/api/debug/status"
            echo "  - Redis:    localhost:6379"
            echo "  - Postgres: localhost:5432"
            echo ""
            echo "📝 Commands:"
            echo "  View logs:    docker-compose logs -f orchestrator"
            echo "  Stop:         docker-compose down"
            echo "  Restart:      docker-compose restart"
        else
            docker-compose logs orchestrator
            docker-compose down
            exit 1
        fi
        ;;
        
    docker)
        echo "🐳 Starting with Docker..."
        
        # Build image
        echo "Building Docker image..."
        docker build -t sct:latest . || {
            echo -e "${RED}❌ Docker build failed${NC}"
            exit 1
        }
        
        # Stop any existing container
        docker stop sct-service 2>/dev/null || true
        docker rm sct-service 2>/dev/null || true
        
        # Run container
        echo "Starting container..."
        docker run \
            --name sct-service \
            -d \
            -p $PORT:8000 \
            --env-file "$ENV_FILE" \
            sct:latest || {
            echo -e "${RED}❌ Docker run failed${NC}"
            exit 1
        }
        
        if check_service $PORT; then
            echo ""
            echo -e "${GREEN}🎉 SCT is running with Docker!${NC}"
            echo ""
            echo "📊 Service endpoints:"
            echo "  - API:    http://localhost:$PORT"
            echo "  - Docs:   http://localhost:$PORT/docs"
            echo "  - Health: http://localhost:$PORT/health"
            echo "  - Debug:  http://localhost:$PORT/api/debug/status"
            echo ""
            echo "📝 Commands:"
            echo "  View logs: docker logs -f sct-service"
            echo "  Stop:      docker stop sct-service"
            echo "  Remove:    docker rm sct-service"
        else
            docker logs sct-service
            docker stop sct-service
            docker rm sct-service
            exit 1
        fi
        ;;
        
    local|*)
        echo "🖥️ Starting locally..."
        
        # Check Python
        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}❌ Python 3 not found${NC}"
            exit 1
        fi
        
        # Check dependencies
        if ! python3 -c "import uvicorn" 2>/dev/null; then
            echo -e "${YELLOW}⚠️ Installing dependencies...${NC}"
            pip install -r requirements.txt || {
                echo -e "${RED}❌ Failed to install dependencies${NC}"
                exit 1
            }
        fi
        
        # Kill any existing process on port
        lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
        
        # Load environment and start
        echo "Starting service on port $PORT..."
        
        # Export environment variables
        export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
        
        # Start in background
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT > sct.log 2>&1 &
        SCT_PID=$!
        
        echo "Process started with PID: $SCT_PID"
        
        if check_service $PORT; then
            echo ""
            echo -e "${GREEN}🎉 SCT is running locally!${NC}"
            echo ""
            echo "📊 Service endpoints:"
            echo "  - API:    http://localhost:$PORT"
            echo "  - Docs:   http://localhost:$PORT/docs"
            echo "  - Health: http://localhost:$PORT/health"
            echo "  - Debug:  http://localhost:$PORT/api/debug/status"
            echo ""
            echo "📝 Commands:"
            echo "  View logs: tail -f sct.log"
            echo "  Stop:      kill $SCT_PID"
            echo ""
            echo "PID saved to sct.pid"
            echo $SCT_PID > sct.pid
        else
            echo -e "${RED}❌ Service failed to start${NC}"
            echo "Check sct.log for details"
            kill $SCT_PID 2>/dev/null || true
            tail -20 sct.log
            exit 1
        fi
        ;;
esac

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ Startup complete!${NC}"
echo -e "${GREEN}============================================${NC}"