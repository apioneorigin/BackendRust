#!/bin/bash
#
# Claude HTML Frontend Startup Script
#
# Starts:
# - Python/FastAPI backend on port 8000 (with SQLite for local dev)
# - Simple proxy server on port 5173 serving Claude_HTML.html
#
# This serves the standalone Claude_HTML.html file and proxies
# API requests to the backend.
#

cd "$(dirname "$0")"

BACKEND_PORT=8000
FRONTEND_PORT=5173
SCRIPT_PID=$$

echo "============================================"
echo "  Claude HTML Frontend Development Server"
echo "============================================"
echo ""

# Kill existing processes on ports
echo "[1/5] Stopping existing services on ports..."
lsof -ti :$BACKEND_PORT | xargs -r kill -9 2>/dev/null
lsof -ti :$FRONTEND_PORT | xargs -r kill -9 2>/dev/null

# Kill any existing node/python dev processes (but not this script)
echo "[2/5] Cleaning up old processes..."
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "html_proxy_server.py" 2>/dev/null

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
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies."
        exit 1
    fi
    cd ..
    echo "    Backend environment ready!"
else
    echo "    Backend venv found."
fi

# Create the proxy server script
echo "[4/5] Setting up proxy server..."
cat > /tmp/html_proxy_server.py << 'PROXY_SCRIPT'
#!/usr/bin/env python3
"""
Simple HTTP server that serves Claude_HTML.html and proxies /api/* to backend
"""
import http.server
import socketserver
import urllib.request
import urllib.error
import os
import sys

BACKEND_URL = "http://localhost:8000"
HTML_FILE = sys.argv[1] if len(sys.argv) > 1 else "Claude_HTML.html"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5173

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            self.proxy_request('GET')
        elif self.path == '/' or self.path == '/index.html':
            self.serve_html()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.proxy_request('POST')
        else:
            self.send_error(404, "Not Found")

    def serve_html(self):
        try:
            with open(HTML_FILE, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f"File not found: {HTML_FILE}")

    def proxy_request(self, method):
        target_url = f"{BACKEND_URL}{self.path}"

        # Read request body for POST
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        try:
            req = urllib.request.Request(target_url, data=body, method=method)

            # Copy relevant headers
            for header in ['Content-Type', 'Accept', 'Authorization']:
                if header in self.headers:
                    req.add_header(header, self.headers[header])

            # Make request to backend
            with urllib.request.urlopen(req) as response:
                # Send response status
                self.send_response(response.status)

                # Copy response headers
                for header, value in response.getheaders():
                    if header.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(header, value)
                self.end_headers()

                # Stream response body
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(e.read())
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Backend connection error: {e.reason}".encode())

    def log_message(self, format, *args):
        print(f"[Proxy] {args[0]}")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(HTML_FILE)) or '.')

    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"Serving {HTML_FILE} at http://localhost:{PORT}")
        print(f"Proxying /api/* to {BACKEND_URL}")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()
PROXY_SCRIPT

echo "    Proxy server script created."

sleep 1

echo "[5/5] Starting servers..."

# Start backend
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
    echo "No GUI terminal found, starting backend in background..."
    cd backend && source venv/bin/activate && export USE_SQLITE=true && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
    cd ..
fi

sleep 3

# Start proxy server for HTML frontend
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell app \"Terminal\" to do script \"cd '$(pwd)' && source backend/venv/bin/activate && echo '' && echo '========================================' && echo '  HTML Frontend on port $FRONTEND_PORT' && echo '========================================' && echo '' && python /tmp/html_proxy_server.py '$(pwd)/Claude_HTML.html' $FRONTEND_PORT\"" 2>/dev/null
elif command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="HTML Frontend" -- bash -c "cd '$(pwd)' && source backend/venv/bin/activate && echo 'Starting HTML Frontend on port $FRONTEND_PORT...' && python /tmp/html_proxy_server.py '$(pwd)/Claude_HTML.html' $FRONTEND_PORT; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -title "HTML Frontend" -e "cd '$(pwd)' && source backend/venv/bin/activate && python /tmp/html_proxy_server.py '$(pwd)/Claude_HTML.html' $FRONTEND_PORT" &
else
    source backend/venv/bin/activate && python /tmp/html_proxy_server.py "$(pwd)/Claude_HTML.html" $FRONTEND_PORT &
fi

echo ""
echo "============================================"
echo "  Services Starting..."
echo "============================================"
echo ""
echo "  HTML Frontend: http://localhost:$FRONTEND_PORT"
echo "  Backend API:   http://localhost:$BACKEND_PORT"
echo "  API Docs:      http://localhost:$BACKEND_PORT/docs"
echo ""
echo "  Database: SQLite (backend/data/dev.db)"
echo ""
echo "  The HTML frontend proxies /api/* to backend"
echo "  Open http://localhost:$FRONTEND_PORT to test"
echo ""
echo "============================================"
