#!/bin/bash
# Start Reality Transformer Backend

# Change to backend directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: No .env file found!"
    echo "Copy .env.example to .env and add your OpenAI API key:"
    echo "  cp .env.example .env"
    echo ""
    echo "Starting without OpenAI (fallback mode)..."
fi

# Start the server
echo ""
echo "Starting Reality Transformer on http://localhost:3000"
echo "Press Ctrl+C to stop"
echo ""

python -m uvicorn main:app --host 0.0.0.0 --port 3000 --reload
