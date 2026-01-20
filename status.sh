#!/bin/bash
#
# Reality Transformer - Status Script
# Shows status of all services
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$PROJECT_ROOT/.pids"

echo -e "${BLUE}Reality Transformer - Service Status${NC}"
echo "════════════════════════════════════════"

# Check backend
echo -n "Backend (port 3000):  "
if [ -f "$PID_DIR/backend.pid" ]; then
    pid=$(cat "$PID_DIR/backend.pid" 2>/dev/null)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo -e "${GREEN}Running${NC} (PID: $pid)"

        # Try to get health status
        health=$(curl -s http://localhost:3000/health 2>/dev/null)
        if [ -n "$health" ]; then
            formula_count=$(echo "$health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('formula_count', 'N/A'))" 2>/dev/null || echo "N/A")
            openai=$(echo "$health" | python3 -c "import sys,json; print('Yes' if json.load(sys.stdin).get('openai_configured') else 'No')" 2>/dev/null || echo "N/A")
            echo "                      Formulas: $formula_count | OpenAI: $openai"
        fi
    else
        echo -e "${RED}Stopped${NC} (stale PID file)"
    fi
else
    # Check if port is in use anyway
    if curl -s http://localhost:3000/health &>/dev/null; then
        echo -e "${YELLOW}Running${NC} (no PID file)"
    else
        echo -e "${RED}Stopped${NC}"
    fi
fi

echo ""
echo "════════════════════════════════════════"
echo "Frontend URL: http://localhost:3000"
echo "Health URL:   http://localhost:3000/health"
