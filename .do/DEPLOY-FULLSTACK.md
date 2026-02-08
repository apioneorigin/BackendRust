# Deploy Full Stack App (Frontend + Backend)

## Overview

This configuration deploys:
- **Frontend**: SvelteKit app on port 3000
- **Backend**: FastAPI API on port 8000
- **Databases**: PostgreSQL + Redis

## Routing

```
https://your-app.ondigitalocean.app/          → Frontend (SvelteKit)
https://your-app.ondigitalocean.app/api/      → Backend (FastAPI)
```

## Quick Deploy

### 1. Update App Spec in DigitalOcean

1. Go to **DigitalOcean Console** → **Apps** → Your app
2. Click **Settings** → **App Spec**
3. Click **Edit**
4. Copy the contents of `.do/app-fullstack.yaml`
5. Paste and **Save**

### 2. Set Environment Variables

Go to **Settings** → **Environment Variables** and set these for the **backend** service:

```
OPENAI_API_KEY = your-new-openai-key
ANTHROPIC_API_KEY = your-new-anthropic-key
JWT_SECRET = (from: openssl rand -hex 32)
DATABASE_URL = postgresql://doadmin:YOUR_PASSWORD@db-postgresql-nyc1-83404-do-user-33112092-0.m.db.ondigitalocean.com:25060/defaultdb?sslmode=require
REDIS_URL = rediss://default:YOUR_PASSWORD@db-valkey-nyc1-88974-do-user-33112092-0.m.db.ondigitalocean.com:25061
```

**Note:** Frontend environment variables are auto-generated using `${backend.PUBLIC_URL}` references.

### 3. Deploy

Click **Deploy** and wait for both services to build.

## What Gets Deployed

### Frontend Service

- **Name**: `frontend`
- **Port**: 3000
- **Build**: Multi-stage Docker build (Node.js)
- **Source**: `/frontend-svelte` directory
- **Instances**: 1x 0.5GB RAM

**Environment Variables (Auto-set):**
- `BACKEND_URL`: Internal backend URL for server-side calls
- `PUBLIC_API_URL`: Public API URL for browser calls
- `ORIGIN`: Frontend public URL
- `NODE_ENV`: production

### Backend Service

- **Name**: `backend`
- **Port**: 8000
- **Build**: Dockerfile (Python/FastAPI)
- **Source**: `/` (root directory)
- **Route**: `/api` prefix
- **Instances**: 2x 1GB RAM (HA)

**Environment Variables:**
- API keys and secrets (set manually)
- Database connections
- CORS origins (auto-set to frontend URL)

## Verify Deployment

### Check Logs

**Frontend logs:**
```
Listening on 0.0.0.0:3000
```

**Backend logs:**
```
[Database] Using PostgreSQL: db-postgresql-nyc1-83404...
Database initialized
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Test Routes

1. **Frontend**: Visit `https://your-app.ondigitalocean.app/`
   - Should show your SvelteKit UI

2. **Backend API**: Visit `https://your-app.ondigitalocean.app/api/health/`
   - Should return JSON: `{"status": "ok", "app": "Reality Transformer API"}`

3. **Frontend → Backend**: Use your app
   - Frontend should successfully call backend API

## Architecture

```
┌─────────────────────────────────────────────┐
│          DigitalOcean App Platform          │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐      ┌──────────────┐    │
│  │   Frontend   │      │   Backend    │    │
│  │  (SvelteKit) │─────→│   (FastAPI)  │    │
│  │  Port 3000   │      │  Port 8000   │    │
│  └──────────────┘      └───────┬──────┘    │
│         │                      │            │
│         │                      ├───→ PostgreSQL
│         │                      └───→ Redis
│         ↓                                   │
│    User Browser                             │
└─────────────────────────────────────────────┘
```

## Routing Details

DigitalOcean's ingress handles routing:

1. Request to `/` → Routed to `frontend` service
2. Request to `/api/*` → Routed to `backend` service
3. Request to `/about` → Routed to `frontend` service (SvelteKit routing)

## Cost Estimate

- Frontend: 1x apps-s-1vcpu-0.5gb = ~$5/month
- Backend: 2x apps-s-1vcpu-1gb = ~$24/month
- PostgreSQL: Basic = ~$15/month
- Redis: Basic = ~$15/month
- **Total**: ~$59/month

## Troubleshooting

### Frontend Can't Connect to Backend

**Check CORS configuration:**
- Backend should have `CORS_ORIGINS` set to frontend URL
- This is auto-configured with `${frontend.PUBLIC_URL}`

**Check environment variables:**
```bash
# In frontend service logs, verify:
BACKEND_URL=https://backend-xxx.ondigitalocean.app
PUBLIC_API_URL=https://your-app.ondigitalocean.app/api
```

### Backend API 404 Errors

**Verify route prefix:**
- Backend should have `routes: - path: /api` configured
- API calls should use `/api/` prefix

### Frontend Shows 404

**Check build logs:**
- SvelteKit build should complete successfully
- `npm run build` should generate `/build` directory

## Scaling

### Frontend (Low Traffic)
- Current: 1 instance (0.5GB RAM)
- Scale up: Increase to 2 instances for HA
- Or upgrade to 1GB RAM for better performance

### Backend (Database-Heavy)
- Current: 2 instances (1GB RAM each)
- Already configured for HA
- Monitor CPU/memory in DO Console

## Next Steps

After successful deployment:

1. ✅ Test all frontend pages
2. ✅ Test API endpoints from frontend
3. ✅ Verify database connections
4. ⏳ Wait 30-60 min, then switch to VPC hostnames
5. 🌐 Set up custom domain
6. 🔒 Configure SSL (automatic with DO)

---

**Your full-stack app with frontend + backend + databases is now deployed!** 🚀
