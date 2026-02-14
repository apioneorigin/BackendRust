# Deploy Full Stack to DigitalOcean App Platform

Deploys SvelteKit frontend, FastAPI backend, PostgreSQL, and Valkey as a single DO app.

```
https://your-app.ondigitalocean.app/*   -> Frontend (SvelteKit)
                                           hooks.server.ts proxies /api/* to backend internally
```

**CRITICAL: ALL traffic must route through SvelteKit.** Do NOT add a separate
`/api` ingress rule for the backend. The backend must be internal-only (no
public ingress). SvelteKit's `hooks.server.ts` handles API routing, auth
(HttpOnly cookie → Bearer header), and SSE streaming. Routing `/api/*`
directly to the backend bypasses auth and causes 401 errors.

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

# Backend health (routed through SvelteKit proxy)
curl https://your-app.ondigitalocean.app/api/healthz/
```

## Architecture

```
                    DO App Platform
   ┌─────────────────────────────────────────┐
   │              Ingress Router              │
   │          /*  ->  frontend                │
   │   (backend has NO public ingress)        │
   ├──────────────────────────────────────────┤
   │  Frontend (SvelteKit :3000)              │
   │  ┌────────────────────────────────────┐  │
   │  │ hooks.server.ts                    │  │
   │  │  /api/* → proxy to backend         │  │
   │  │  (strips /api, adds Bearer token,  │  │
   │  │   streams SSE natively)            │  │
   │  └──────────────┬─────────────────────┘  │
   │                 │ internal (PRIVATE_URL)  │
   │  ┌──────────────▼─────────────────────┐  │
   │  │ Backend (FastAPI :8000)            │  │
   │  │ internal-only — no public ingress  │  │
   │  └──────────────┬─────────────────────┘  │
   └─────────────────┼────────────────────────┘
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
| API returns 401 | Verify the ingress has ONLY one rule: `/ → frontend`. Remove any `/api → backend` route. The backend must be internal-only. |
| Frontend can't reach backend | Check `BACKEND_URL` in frontend env vars — must be `${backend.PRIVATE_URL}` |
| CORS errors in browser | Verify `CORS_ORIGINS` matches `${APP_URL}` |
| API returns 404 | Check `BACKEND_URL` resolves. Verify backend is running (check runtime logs). Do NOT add a `/api` ingress route — that bypasses auth. |
| Session store warning | Check `REDIS_URL` resolves — verify valkey database component is attached |
| `DATABASE_URL` empty | Verify cluster name in `databases:` section matches your actual cluster |
| Build fails (frontend) | Check `npm run build` locally in `frontend-svelte/` |
| Build fails (backend) | Check `docker build -t test .` locally from repo root |

## Verify Correct Ingress Configuration

Run this in your terminal to check the app spec:

```bash
doctl apps spec get <your-app-id> | grep -A5 'ingress'
```

You should see ONLY ONE rule:

```yaml
ingress:
  rules:
    - component:
        name: frontend
      match:
        path:
          prefix: /
```

If you see a second rule routing `/api` to `backend`, **remove it** — that is
the root cause of 401 errors.

## Cost Estimate

- Frontend 1x 0.5GB: ~$5/mo
- Backend 1x 1GB: ~$12/mo
- PostgreSQL Managed: ~$15/mo
- Valkey Managed: ~$15/mo
- **Total**: ~$47/mo
