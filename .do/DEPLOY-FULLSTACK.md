# Deploy Full Stack to DigitalOcean App Platform

Deploys SvelteKit frontend, FastAPI backend, PostgreSQL, and Valkey as a single DO app.

```
https://your-app.ondigitalocean.app/        -> Frontend (SvelteKit)
https://your-app.ondigitalocean.app/api/*   -> Backend  (FastAPI)
```

## 1. Create the App

1. **DO Console** -> **Apps** -> **Create App**
2. Source: **GitHub** -> `apioneorigin/BackendRust`, branch `main`
3. Click **Edit App Spec** and paste the contents of `.do/app-fullstack.yaml`
4. Save and proceed

The app spec includes PostgreSQL and Valkey database components. DO will create managed database clusters automatically.

> **Using existing databases?** Add `cluster_name: your-cluster-name` under each database entry in the spec to attach existing clusters instead of creating new ones.

## 2. Set Secret Environment Variables

Go to **Settings** -> **backend** component -> **Environment Variables** and set:

| Variable | Value |
|----------|-------|
| `OPENAI_API_KEY` | your OpenAI key |
| `ANTHROPIC_API_KEY` | your Anthropic key |
| `JWT_SECRET` | output of `openssl rand -hex 32` |
| `TAVILY_API_KEY` | your Tavily key (optional — enables cheaper web search) |

`DATABASE_URL` and `REDIS_URL` are auto-wired from the database components via `${db.DATABASE_URL}` and `${cache.DATABASE_URL}` — no manual copy/paste needed.

Frontend env vars (`BACKEND_URL`, `PUBLIC_API_URL`, `ORIGIN`) are auto-wired via `${APP_URL}` and `${backend.PRIVATE_URL}` references in the spec.

## 3. Deploy and Verify

Save variables. Both services build and deploy automatically.

### Check logs

**Frontend** should show:
```
Listening on 0.0.0.0:3000
```

**Backend** should show:
```
[Database] Using PostgreSQL: ...
[SESSION STORE] Connected to Redis — sessions persist across restarts
[CACHE] Connected to Redis
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Test endpoints

```bash
# Frontend
curl -I https://your-app.ondigitalocean.app/

# Backend health
curl https://your-app.ondigitalocean.app/api/health/
```

## Architecture

```
                    DO App Platform
   ┌─────────────────────────────────────────┐
   │              Ingress Router              │
   │   /  -> frontend    /api -> backend     │
   ├──────────────┬──────────────────────────┤
   │  Frontend    │    Backend               │
   │  SvelteKit   │    FastAPI               │
   │  :3000       │    :8000                 │
   │  0.5GB       │    1GB                   │
   └──────────────┴───────┬──────────────────┘
                          │
                  ┌───────┴───────┐
                  │  PostgreSQL   │
                  │  Valkey       │
                  └───────────────┘
```

## 4. Post-Deploy

- **Custom domain**: Settings -> Domains
- **Scale backend**: Increase `instance_count` in app spec
- **Scale frontend**: Usually 1 instance is fine; add more if needed

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Frontend can't reach backend | Check `BACKEND_URL` in frontend env vars |
| CORS errors in browser | Verify `CORS_ORIGINS` matches `${APP_URL}` |
| API returns 404 | Ensure ingress routes `/api` to backend component |
| Session store warning | Check `REDIS_URL` resolves — verify `cache` database component is attached |
| Build fails (frontend) | Check `npm run build` locally in `frontend-svelte/` |
| Build fails (backend) | Check `docker build -t test .` locally from repo root |

## Cost Estimate

- Frontend 1x 0.5GB: ~$5/mo
- Backend 1x 1GB: ~$12/mo
- PostgreSQL Managed: ~$15/mo
- Valkey Managed: ~$15/mo
- **Total**: ~$47/mo
