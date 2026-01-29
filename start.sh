#!/bin/bash
#
# Reality Transformer - Master Startup Script
# Kills existing servers and starts fresh
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
FRONTEND_DIR="$PROJECT_ROOT/frontend-svelte"
LOG_DIR="$PROJECT_ROOT/logs"

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=5173

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

# Function to kill process on port
kill_port() {
    local port=$1
    local pids=""

    # Try lsof first
    if command -v lsof &> /dev/null; then
        pids=$(lsof -ti :$port 2>/dev/null || true)
    fi

    # Try fuser as fallback
    if [ -z "$pids" ] && command -v fuser &> /dev/null; then
        pids=$(fuser $port/tcp 2>/dev/null || true)
    fi

    if [ -n "$pids" ]; then
        echo -e "  ${YELLOW}Killing processes on port $port: $pids${NC}"
        for pid in $pids; do
            kill -9 $pid 2>/dev/null || true
        done
        sleep 1
    fi
}

# Function to stop all services
stop_all() {
    echo -e "${YELLOW}Stopping all running services...${NC}"

    # Kill by PID files
    for service in backend frontend; do
        if [ -f "$PID_DIR/$service.pid" ]; then
            local pid=$(cat "$PID_DIR/$service.pid" 2>/dev/null)
            if [ -n "$pid" ]; then
                echo "  Stopping $service (PID: $pid)..."
                kill -9 "$pid" 2>/dev/null || true
            fi
            rm -f "$PID_DIR/$service.pid"
        fi
    done

    # Kill any process on our ports
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT

    echo -e "  ${GREEN}All services stopped${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        lsof -i :$port &> /dev/null
    elif command -v netstat &> /dev/null; then
        netstat -tuln | grep -q ":$port "
    else
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

# Function to setup Python environment
setup_python() {
    echo -e "${BLUE}Setting up Python environment...${NC}"

    cd "$BACKEND_DIR"

    if [ ! -d "venv" ]; then
        echo "  Creating virtual environment..."
        python3 -m venv venv
    fi

    source venv/bin/activate

    echo "  Installing dependencies..."
    pip install -q -r requirements.txt 2>/dev/null

    echo -e "  ${GREEN}Python environment ready${NC}"
}

# Function to setup Node environment
setup_node() {
    echo -e "${BLUE}Setting up Node environment...${NC}"

    cd "$FRONTEND_DIR"

    if [ ! -d "node_modules" ]; then
        echo "  Installing npm dependencies..."
        npm install
    fi

    echo -e "  ${GREEN}Node environment ready${NC}"
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
    return 1
}

# Function to start the backend
start_backend() {
    echo -e "${BLUE}Starting Python Backend...${NC}"

    cd "$BACKEND_DIR"
    source venv/bin/activate

    nohup python -m uvicorn main:app \
        --host 0.0.0.0 \
        --port $BACKEND_PORT \
        > "$LOG_DIR/backend.log" 2>&1 &

    local pid=$!
    echo $pid > "$PID_DIR/backend.pid"

    echo "  Backend starting (PID: $pid)..."

    if wait_for_service $BACKEND_PORT "Backend"; then
        echo -e "  ${GREEN}Backend running on http://localhost:$BACKEND_PORT${NC}"
        return 0
    else
        echo -e "  ${RED}Backend failed to start. Check $LOG_DIR/backend.log${NC}"
        return 1
    fi
}

# Function to start the frontend
start_frontend() {
    echo -e "${BLUE}Starting SvelteKit Frontend...${NC}"

    cd "$FRONTEND_DIR"

    nohup npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT \
        > "$LOG_DIR/frontend.log" 2>&1 &

    local pid=$!
    echo $pid > "$PID_DIR/frontend.pid"

    echo "  Frontend starting (PID: $pid)..."

    if wait_for_service $FRONTEND_PORT "Frontend"; then
        echo -e "  ${GREEN}Frontend running on http://localhost:$FRONTEND_PORT${NC}"
        return 0
    else
        echo -e "  ${RED}Frontend failed to start. Check $LOG_DIR/frontend.log${NC}"
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
    echo "  Frontend:  http://localhost:$FRONTEND_PORT"
    echo "  Backend:   http://localhost:$BACKEND_PORT"
    echo "  Health:    http://localhost:$BACKEND_PORT/health"
    echo ""
    echo -e "${YELLOW}Logs:${NC}"
    echo "  Backend:   tail -f $LOG_DIR/backend.log"
    echo "  Frontend:  tail -f $LOG_DIR/frontend.log"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  Restart:   $PROJECT_ROOT/start.sh"
    echo "  Stop all:  $PROJECT_ROOT/stop.sh"
    echo ""
}

# Main execution
main() {
    cd "$PROJECT_ROOT"

    # Always stop existing services first
    stop_all

    setup_python
    setup_node
    check_openai || true
    start_backend
    start_frontend
    show_status
}

# Handle Ctrl+C
trap 'echo -e "\n${YELLOW}Startup interrupted${NC}"; exit 1' INT

# Run main
main "$@"
