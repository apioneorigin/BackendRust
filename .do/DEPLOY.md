# Deploy Backend Only to DigitalOcean App Platform

## 1. Create Databases

### PostgreSQL

1. **DO Console** -> **Databases** -> **Create Database Cluster**
2. Engine: **PostgreSQL 18** (or latest available)
3. Region: **NYC** (same as app)
4. Plan: Basic ($15/mo) or whatever fits your needs
5. Wait for status: **Online**
6. Note the **cluster name** (e.g. `db-postgresql-nyc-12345`)

### Redis / Valkey (optional)

1. **DO Console** -> **Databases** -> **Create Database Cluster**
2. Engine: **Valkey 8** (or Redis)
3. Region: **NYC**
4. Plan: Basic ($15/mo)
5. Note the **cluster name** (e.g. `db-valkey-nyc-12345`)

## 2. Create the App

1. **DO Console** -> **Apps** -> **Create App**
2. Source: **GitHub** -> select `apioneorigin/BackendRust`, branch `main`
3. Click **Edit App Spec** and paste the contents of `.do/app.yaml`
4. **Replace the placeholder cluster names** in the `databases:` section:
   - `<your-pg-cluster>` -> your PostgreSQL cluster name from step 1
   - `<your-valkey-cluster>` -> your Valkey cluster name from step 1
5. Save and proceed

## 3. Set Secret Environment Variables

Go to **Settings** -> **backend** component -> **Environment Variables** and set:

| Variable | Value | Notes |
|----------|-------|-------|
| `OPENAI_API_KEY` | your key | from platform.openai.com |
| `ANTHROPIC_API_KEY` | your key | from console.anthropic.com |
| `JWT_SECRET` | `openssl rand -hex 32` | generate fresh |

`DATABASE_URL` and `REDIS_URL` are **auto-injected** from the attached database components via `${db.DATABASE_URL}` and `${valkey.DATABASE_URL}` — no manual copy/paste of connection strings needed.

> **How it works:** The `databases:` section in the app spec attaches your managed clusters. DigitalOcean resolves `${db.DATABASE_URL}` and `${valkey.DATABASE_URL}` at deploy time and injects them as environment variables. The backend code also has a fallback auto-discovery module (`utils/resolve_do_env.py`) that scans environment variables for PostgreSQL/Redis connection strings in case the binding is missing.

## 4. Trusted Sources

After creating the app, add it to each database cluster's firewall:

1. **DO Console** -> **Databases** -> select your cluster
2. **Settings** -> **Trusted Sources** -> **Add** your app

Repeat for both PostgreSQL and Valkey clusters.

## 5. Deploy

Save the environment variables. The app will build and deploy automatically.

### Verify

Check **Runtime Logs** for:

```
[Database] Using PostgreSQL: your-host...
Database initialized
[CACHE] Connected to Redis
INFO: Uvicorn running on http://0.0.0.0:8000
```

Test the health endpoint:

```
curl https://your-app.ondigitalocean.app/health
```

## 6. Post-Deploy

- **Custom domain**: Settings -> Domains -> Add Domain
- **VPC networking**: Once databases are fully provisioned, switch to `private-` hostnames for lower latency
- **Scaling**: Increase `instance_count` in app spec if needed (keep single uvicorn process per instance)

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Build fails | Check Dockerfile builds locally: `docker build -t test .` |
| Health check fails | Verify `/healthz/` endpoint returns 200. Check runtime logs |
| DB connection refused | Ensure database is Online and Trusted Sources includes your app |
| DB auth failure | Check cluster name in `databases:` section matches your actual cluster |
| `DATABASE_URL` empty | Verify cluster name is correct and database component shows as attached |
| Timeout on startup | Increase `initial_delay_seconds` in health check |

## Cost Estimate

- App Platform 1x 1vCPU/1GB: ~$12/mo
- PostgreSQL Basic: ~$15/mo
- Redis/Valkey Basic: ~$15/mo
- **Total**: ~$42/mo
