import sys
from pathlib import Path

# Add backend to path so imports work
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the FastAPI app
from main import app

# Vercel expects the app to be named 'app' or 'handler'
