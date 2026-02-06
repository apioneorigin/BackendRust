#!/bin/bash
#
# BackendRust Development Server Startup Script
#
# Starts:
# - Python/FastAPI backend on port 8000 (with SQLite for local dev)
# - SvelteKit frontend on port 5173
#
# Features:
# - Auto-creates Python venv if missing
# - Installs dependencies automatically
# - Kills all existing servers and old terminal windows
# - Uses SQLite for local development (no external database needed)
#
# UI Layout:
# - Unified collapsible sidebar (consistent across all pages)
# - Chat page: 4-box layout with matrix and live preview
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
echo "[1/5] Stopping existing services on ports..."
lsof -ti :$BACKEND_PORT | xargs -r kill -9 2>/dev/null
lsof -ti :$FRONTEND_PORT | xargs -r kill -9 2>/dev/null

# Kill any existing node/python dev processes (but not this script)
echo "[2/5] Cleaning up old processes..."
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

sleep 1

# Check and setup backend venv
echo "[3/5] Checking backend environment..."
if [ ! -d "backend/venv" ]; then
    echo "    Creating Python virtual environment..."
    cd backend
    python3 -m venv venv || python -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create venv. Make sure Python is installed."
        exit 1
    fi
    echo "    Installing dependencies..."
    source venv/bin/activate
    pip install -r backend/requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies."
        exit 1
    fi
    cd ..
    echo "    Backend environment ready!"
else
    echo "    Backend venv found."
fi

# Check frontend node_modules
echo "[4/5] Checking frontend environment..."
if [ ! -d "frontend-svelte/node_modules" ]; then
    echo "    Installing npm dependencies..."
    cd frontend-svelte
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install npm dependencies."
        exit 1
    fi
    cd ..
    echo "    Frontend dependencies ready!"
else
    echo "    Frontend node_modules found."
fi

sleep 1

echo "[5/5] Starting servers..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use osascript with USE_SQLITE
    osascript -e "tell app \"Terminal\" to do script \"cd '$(pwd)/backend' && source venv/bin/activate && export USE_SQLITE=true && echo '' && echo '========================================' && echo '  Backend API starting on port $BACKEND_PORT' && echo '  Database: SQLite (local development)' && echo '========================================' && echo '' && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload\"" 2>/dev/null
elif command -v gnome-terminal &> /dev/null; then
    # Linux with GNOME
    gnome-terminal --title="Backend API" -- bash -c "cd '$(pwd)/backend' && source venv/bin/activate && export USE_SQLITE=true && echo 'Starting Backend API on port $BACKEND_PORT...' && echo 'Database: SQLite (local development)' && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload; exec bash"
elif command -v xterm &> /dev/null; then
    # Fallback to xterm
    xterm -title "Backend API" -e "cd '$(pwd)/backend' && source venv/bin/activate && export USE_SQLITE=true && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload" &
else
    # No GUI terminal, run in background
    echo "No GUI terminal found, starting in background..."
    cd backend && source venv/bin/activate && export USE_SQLITE=true && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
    cd ..
fi

sleep 3

if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell app \"Terminal\" to do script \"cd '$(pwd)/frontend-svelte' && echo '' && echo '========================================' && echo '  Frontend starting on port $FRONTEND_PORT' && echo '========================================' && echo '' && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT\"" 2>/dev/null
elif command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="Frontend SvelteKit" -- bash -c "cd '$(pwd)/frontend-svelte' && echo 'Starting SvelteKit Frontend on port $FRONTEND_PORT...' && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT; exec bash"
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
echo "  Database: SQLite (backend/data/dev.db)"
echo ""
echo "  UI Layout:"
echo "  - Collapsible sidebar (all pages)"
echo "  - Chat: 4-box grid with matrix"
echo "  - Documents, Settings: Content area"
echo ""
echo "============================================"
