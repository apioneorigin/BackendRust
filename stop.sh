#!/bin/bash
#
# Reality Transformer - Stop Script
# Stops all running services
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$PROJECT_ROOT/.pids"

echo -e "${YELLOW}Stopping Reality Transformer services...${NC}"

stopped=0

# Stop backend
if [ -f "$PID_DIR/backend.pid" ]; then
    pid=$(cat "$PID_DIR/backend.pid" 2>/dev/null)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo "  Stopping backend (PID: $pid)..."
        kill "$pid" 2>/dev/null
        sleep 1
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null
        fi
        stopped=$((stopped + 1))
    fi
    rm -f "$PID_DIR/backend.pid"
fi

# Also try to free the port if something is still listening
if command -v fuser &> /dev/null; then
    fuser -k 3000/tcp 2>/dev/null && stopped=$((stopped + 1))
fi

if [ $stopped -gt 0 ]; then
    echo -e "${GREEN}All services stopped${NC}"
else
    echo -e "${YELLOW}No running services found${NC}"
fi
