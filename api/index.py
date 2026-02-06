import sys
from pathlib import Path

# Add backend to path so imports work.
# Handles both local dev (api/ is sibling of backend/) and
# Vercel Build Output API (backend/ is copied into the function directory).
here = Path(__file__).parent
backend_candidates = [
    here / "backend",          # Vercel Build Output API: backend/ in same dir as index.py
    here.parent / "backend",   # Local dev: api/ is sibling of backend/
]
for candidate in backend_candidates:
    if candidate.exists():
        sys.path.insert(0, str(candidate))
        break

# Import the FastAPI app
from main import app

# Vercel expects the app to be named 'app' or 'handler'
