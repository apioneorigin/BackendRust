#!/bin/bash
#
# BackendRust Development Server Startup Script
#
# Starts:
# - Python/FastAPI backend on port 8000
# - SvelteKit frontend on port 5173 (unified 4-box layout with embedded matrix)
#
# Features:
# - Kills all existing servers and old terminal windows
# - Starts fresh instances in new terminal windows
#

cd "$(dirname "$0")"

BACKEND_PORT=8000
FRONTEND_PORT=5173
SCRIPT_PID=$$

echo "============================================"
echo "  BackendRust Development Server"
echo "============================================"
echo ""

# Kill existing processes on ports
echo "[1/4] Stopping existing services on ports..."
lsof -ti :$BACKEND_PORT | xargs -r kill -9 2>/dev/null
lsof -ti :$FRONTEND_PORT | xargs -r kill -9 2>/dev/null

# Kill any existing node/python dev processes (but not this script)
echo "[2/4] Cleaning up old processes..."
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "vite.*--port $FRONTEND_PORT" 2>/dev/null
pkill -f "npm run dev.*$FRONTEND_PORT" 2>/dev/null

# Kill old terminal windows running our servers (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e '
        tell application "Terminal"
            set windowList to windows
            repeat with w in windowList
                repeat with t in tabs of w
                    set tabProcs to processes of t
                    if tabProcs contains "uvicorn" or tabProcs contains "vite" or tabProcs contains "npm" then
                        close t
                    end if
                end repeat
            end repeat
        end tell
    ' 2>/dev/null
fi

sleep 2

echo "[3/4] Starting backend server..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use osascript
    osascript -e "tell app \"Terminal\" to do script \"cd '$(pwd)/backend' && source venv/bin/activate && echo 'Starting Backend API...' && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload\"" 2>/dev/null
elif command -v gnome-terminal &> /dev/null; then
    # Linux with GNOME
    gnome-terminal --title="Backend API" -- bash -c "cd '$(pwd)/backend' && source venv/bin/activate && echo 'Starting Backend API...' && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload; exec bash"
elif command -v xterm &> /dev/null; then
    # Fallback to xterm
    xterm -title "Backend API" -e "cd '$(pwd)/backend' && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload" &
else
    # No GUI terminal, run in background
    echo "No GUI terminal found, starting in background..."
    cd backend && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
    cd ..
fi

sleep 2

echo "[4/4] Starting frontend server..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell app \"Terminal\" to do script \"cd '$(pwd)/frontend-svelte' && echo 'Starting SvelteKit Frontend...' && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT\"" 2>/dev/null
elif command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="Frontend SvelteKit" -- bash -c "cd '$(pwd)/frontend-svelte' && echo 'Starting SvelteKit Frontend...' && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -title "Frontend SvelteKit" -e "cd '$(pwd)/frontend-svelte' && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT" &
else
    cd frontend-svelte && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT &
    cd ..
fi

echo ""
echo "============================================"
echo "  Services Starting..."
echo "============================================"
echo ""
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  Backend:  http://localhost:$BACKEND_PORT"
echo "  API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "  Layout: Unified 4-box with embedded matrix"
echo "  - Sidebar: Conversation history"
echo "  - Chat: Response container + Input panel"
echo "  - Matrix: 5x5 transformation grid"
echo "  - Preview: Live coherence metrics"
echo ""
echo "============================================"
