#!/bin/bash
cd "$(dirname "$0")"

BACKEND_PORT=8000
FRONTEND_PORT=5173

echo "Stopping existing services..."
lsof -ti :$BACKEND_PORT | xargs -r kill -9 2>/dev/null
lsof -ti :$FRONTEND_PORT | xargs -r kill -9 2>/dev/null
sleep 1

echo "Starting services..."
osascript -e "tell app \"Terminal\" to do script \"cd $(pwd)/backend && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT\"" 2>/dev/null || \
gnome-terminal -- bash -c "cd $(pwd)/backend && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT; exec bash" 2>/dev/null || \
xterm -e "cd $(pwd)/backend && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT" &

osascript -e "tell app \"Terminal\" to do script \"cd $(pwd)/frontend-svelte && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT\"" 2>/dev/null || \
gnome-terminal -- bash -c "cd $(pwd)/frontend-svelte && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT; exec bash" 2>/dev/null || \
xterm -e "cd $(pwd)/frontend-svelte && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT" &

echo ""
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Backend:  http://localhost:$BACKEND_PORT"
