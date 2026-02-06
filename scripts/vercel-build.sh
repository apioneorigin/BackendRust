#!/bin/bash
set -e

echo "=== Building SvelteKit frontend ==="
cd frontend-svelte
npm install
npm run build
cd ..

echo "=== Setting up Python API function in Build Output ==="
FUNC_DIR="frontend-svelte/.vercel/output/functions/api.func"
mkdir -p "$FUNC_DIR"

# Copy the Python entry point
cp api/index.py "$FUNC_DIR/"

# Copy backend code
cp -r backend "$FUNC_DIR/"

# Copy knowledge base text files used by the LLM
for f in \
    "LLM_Call_1.txt" \
    "LLM_Call_2.txt" \
    "Goal_Discovery_Call_1.txt" \
    "Goal_Discovery_Call_2.txt" \
    "Goal_Discovery_OOF_Reference.txt" \
    "OOF_Math.txt" \
    "OOF_Nomenclature.txt" \
    "Articulation Bridge Rules.txt" \
    "Reverse Causality Mapping Principle.txt" \
    "The Evidence Validation Principle.txt"
do
    [ -f "$f" ] && cp "$f" "$FUNC_DIR/" && echo "  Copied $f"
done

# Copy the insight generation rulebook from backend
[ -f "backend/insight-generation-rulebook.txt" ] && cp "backend/insight-generation-rulebook.txt" "$FUNC_DIR/backend/"

# Install Python dependencies into the function directory
echo "=== Installing Python dependencies ==="
pip install -r api/requirements.txt -t "$FUNC_DIR" --no-cache-dir --quiet 2>&1 || \
    pip3 install -r api/requirements.txt -t "$FUNC_DIR" --no-cache-dir --quiet 2>&1

# Create .vc-config.json for the Python serverless function
cat > "$FUNC_DIR/.vc-config.json" << 'VCEOF'
{
  "runtime": "python3.11",
  "handler": "index.py",
  "launcherType": "Launcher",
  "maxDuration": 60,
  "memory": 1024,
  "environment": {}
}
VCEOF

echo "=== Updating Build Output routing config ==="
# Add API route to config.json so /api/* requests go to the Python function
node -e "
const fs = require('fs');
const configPath = 'frontend-svelte/.vercel/output/config.json';

let config;
try {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
} catch (e) {
    console.error('Could not read config.json:', e.message);
    config = { version: 3, routes: [] };
}

config.routes = config.routes || [];

// Add API route at the beginning so it takes priority over SvelteKit catch-all
// Match /api and /api/* requests and route them to the Python function
const apiRoute = { src: '/api(?:/(.*))?$', dest: '/api' };

// Remove any existing SvelteKit routes that match /api/* (the Python function handles all API)
config.routes = config.routes.filter(r => {
    if (r.src && r.src.startsWith('/api')) return false;
    return true;
});

// Insert API route at position 0 so it has highest priority
config.routes.unshift(apiRoute);
console.log('Added API route at position 0');

fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
console.log('Config routes:', config.routes.length, 'total');
"

echo "=== Build complete ==="
echo "Output directory contents:"
ls -la "frontend-svelte/.vercel/output/functions/" 2>/dev/null || echo "  No functions directory"
