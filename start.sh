#!/bin/bash
#
# Reality Transformer - Master Startup Script
# Starts all services automatically
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_DIR="$PROJECT_ROOT/logs"

# Ports
BACKEND_PORT=3000

# PID files
PID_DIR="$PROJECT_ROOT/.pids"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           Reality Transformer - Startup Script            ║"
echo "║       Consciousness-Based Transformation Engine           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Function to check if a port is in use
check_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        lsof -i :$port &> /dev/null
    elif command -v netstat &> /dev/null; then
        netstat -tuln | grep -q ":$port "
    else
        # Fallback: try to connect
        (echo > /dev/tcp/localhost/$port) 2>/dev/null
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local port=$1
    local name=$2
    local max_attempts=30
    local attempt=1

    echo -n "  Waiting for $name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if check_port $port; then
            echo -e " ${GREEN}Ready!${NC}"
            return 0
        fi
        sleep 0.5
        attempt=$((attempt + 1))
    done
    echo -e " ${RED}Timeout!${NC}"
    return 1
}

# Function to stop existing services
stop_existing() {
    echo -e "${YELLOW}Checking for existing services...${NC}"

    if [ -f "$PID_DIR/backend.pid" ]; then
        local pid=$(cat "$PID_DIR/backend.pid" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "  Stopping existing backend (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 1
        fi
        rm -f "$PID_DIR/backend.pid"
    fi

    # Also check if port is still in use
    if check_port $BACKEND_PORT; then
        echo -e "  ${YELLOW}Port $BACKEND_PORT still in use, attempting to free...${NC}"
        fuser -k $BACKEND_PORT/tcp 2>/dev/null || true
        sleep 1
    fi
}

# Function to setup Python environment
setup_python() {
    echo -e "${BLUE}Setting up Python environment...${NC}"

    cd "$BACKEND_DIR"

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "  Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install/update dependencies
    echo "  Installing dependencies..."
    pip install -q -r requirements.txt 2>/dev/null

    echo -e "  ${GREEN}Python environment ready${NC}"
}

# Function to check OpenAI configuration
check_openai() {
    if [ -f "$BACKEND_DIR/.env" ]; then
        if grep -q "OPENAI_API_KEY=sk-" "$BACKEND_DIR/.env" 2>/dev/null; then
            echo -e "  ${GREEN}OpenAI API key configured${NC}"
            return 0
        fi
    fi

    echo -e "  ${YELLOW}OpenAI API key not configured (running in fallback mode)${NC}"
    echo -e "  ${YELLOW}To enable AI features: cp backend/.env.example backend/.env${NC}"
    return 1
}

# Function to start the backend
start_backend() {
    echo -e "${BLUE}Starting Python Backend...${NC}"

    cd "$BACKEND_DIR"
    source venv/bin/activate

    # Start uvicorn in background
    nohup python -m uvicorn main:app \
        --host 0.0.0.0 \
        --port $BACKEND_PORT \
        > "$LOG_DIR/backend.log" 2>&1 &

    local pid=$!
    echo $pid > "$PID_DIR/backend.pid"

    echo "  Backend starting (PID: $pid)..."

    # Wait for it to be ready
    if wait_for_service $BACKEND_PORT "Backend"; then
        echo -e "  ${GREEN}Backend running on http://localhost:$BACKEND_PORT${NC}"
        return 0
    else
        echo -e "  ${RED}Backend failed to start. Check $LOG_DIR/backend.log${NC}"
        return 1
    fi
}

# Function to show status
show_status() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}All services started successfully!${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  Frontend:  http://localhost:$BACKEND_PORT"
    echo "  Health:    http://localhost:$BACKEND_PORT/health"
    echo "  Logs:      $LOG_DIR/backend.log"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  View logs:     tail -f $LOG_DIR/backend.log"
    echo "  Stop all:      $PROJECT_ROOT/stop.sh"
    echo "  Check status:  curl http://localhost:$BACKEND_PORT/health"
    echo ""
}

# Main execution
main() {
    cd "$PROJECT_ROOT"

    # Stop any existing services
    stop_existing

    # Setup Python
    setup_python

    # Check OpenAI (non-fatal)
    check_openai || true

    # Start backend
    start_backend

    # Show final status
    show_status
}

# Handle Ctrl+C
trap 'echo -e "\n${YELLOW}Startup interrupted${NC}"; exit 1' INT

# Run main
main "$@"
