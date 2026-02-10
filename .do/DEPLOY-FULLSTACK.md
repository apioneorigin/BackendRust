# Deploy Full Stack to DigitalOcean App Platform

Deploys SvelteKit frontend, FastAPI backend, PostgreSQL, and Valkey as a single DO app.

```
https://your-app.ondigitalocean.app/        -> Frontend (SvelteKit)
https://your-app.ondigitalocean.app/api/*   -> Backend  (FastAPI)
```

## 1. Create Databases

1. **DO Console** -> **Databases** -> **Create Database Cluster**
2. Create a **PostgreSQL 18** (or latest) cluster in **NYC**
3. Create a **Valkey 8** (or Redis) cluster in **NYC**
4. Note both **cluster names** (e.g. `db-postgresql-nyc-12345`, `db-valkey-nyc-12345`)

## 2. Create the App

1. **DO Console** -> **Apps** -> **Create App**
2. Source: **GitHub** -> `apioneorigin/BackendRust`, branch `main`
3. Click **Edit App Spec** and paste the contents of `.do/app-fullstack.yaml`
4. **Replace the placeholder cluster names** in the `databases:` section:
   - `<your-pg-cluster>` -> your PostgreSQL cluster name
   - `<your-valkey-cluster>` -> your Valkey cluster name
5. Save and proceed

`DATABASE_URL` and `REDIS_URL` are auto-injected from the attached database components via `${db.DATABASE_URL}` and `${valkey.DATABASE_URL}` — no manual copy/paste of connection strings needed.

Frontend env vars (`BACKEND_URL`, `PUBLIC_API_URL`, `ORIGIN`) are auto-wired via `${APP_URL}` and `${backend.PRIVATE_URL}` references in the spec.

## 3. Set Secret Environment Variables

Go to **Settings** -> **backend** component -> **Environment Variables** and set:

| Variable | Value |
|----------|-------|
| `OPENAI_API_KEY` | your OpenAI key |
| `ANTHROPIC_API_KEY` | your Anthropic key |
| `JWT_SECRET` | output of `openssl rand -hex 32` |

That's it — only 3 secrets to set manually.

## 4. Trusted Sources

Add the app to each database cluster's firewall:

1. **DO Console** -> **Databases** -> select your cluster
2. **Settings** -> **Trusted Sources** -> **Add** your app

Repeat for both PostgreSQL and Valkey clusters.

## 5. Deploy and Verify

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
                  │  PostgreSQL   │  (auto-injected DATABASE_URL)
                  │  Valkey       │  (auto-injected REDIS_URL)
                  └───────────────┘
```

## 6. Post-Deploy

- **Custom domain**: Settings -> Domains
- **Scale backend**: Increase `instance_count` in app spec
- **Scale frontend**: Usually 1 instance is fine; add more if needed

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Frontend can't reach backend | Check `BACKEND_URL` in frontend env vars |
| CORS errors in browser | Verify `CORS_ORIGINS` matches `${APP_URL}` |
| API returns 404 | Ensure ingress routes `/api` to backend component |
| Session store warning | Check `REDIS_URL` resolves — verify valkey database component is attached |
| `DATABASE_URL` empty | Verify cluster name in `databases:` section matches your actual cluster |
| Build fails (frontend) | Check `npm run build` locally in `frontend-svelte/` |
| Build fails (backend) | Check `docker build -t test .` locally from repo root |

## Cost Estimate

- Frontend 1x 0.5GB: ~$5/mo
- Backend 1x 1GB: ~$12/mo
- PostgreSQL Managed: ~$15/mo
- Valkey Managed: ~$15/mo
- **Total**: ~$47/mo
