# Deploy Backend Only to DigitalOcean App Platform

## 1. Create Databases

### PostgreSQL

1. **DO Console** -> **Databases** -> **Create Database Cluster**
2. Engine: **PostgreSQL 16**
3. Region: **NYC** (same as app)
4. Plan: Basic ($15/mo) or whatever fits your needs
5. Wait for status: **Online**
6. Copy the **connection string** from Connection Details

### Redis / Valkey (optional)

1. **DO Console** -> **Databases** -> **Create Database Cluster**
2. Engine: **Redis** (or Valkey)
3. Region: **NYC**
4. Plan: Basic ($15/mo)
5. Copy the **connection string** from Connection Details

## 2. Create the App

1. **DO Console** -> **Apps** -> **Create App**
2. Source: **GitHub** -> select `apioneorigin/BackendRust`, branch `main`
3. Click **Edit App Spec** and paste the contents of `.do/app.yaml`
4. Save and proceed

## 3. Set Secret Environment Variables

Go to **Settings** -> **backend** component -> **Environment Variables** and set:

| Variable | Value | Notes |
|----------|-------|-------|
| `OPENAI_API_KEY` | your key | from platform.openai.com |
| `ANTHROPIC_API_KEY` | your key | from console.anthropic.com |
| `JWT_SECRET` | `openssl rand -hex 32` | generate fresh |
| `DATABASE_URL` | connection string | from step 1 |
| `REDIS_URL` | connection string | from step 1 (optional) |

All are marked `type: SECRET` so they won't appear in logs.

### Database URL format

```
postgresql://user:password@host:25060/defaultdb?sslmode=require
```

Use the **public** hostname initially. Switch to `private-` prefix later for faster VPC networking.

### Redis URL format

```
rediss://default:password@host:25061
```

Note the double `s` in `rediss://` -- this means TLS.

## 4. Deploy

Save the environment variables. The app will build and deploy automatically.

### Verify

Check **Runtime Logs** for:

```
[Database] Using PostgreSQL: your-host...
Database initialized
INFO: Uvicorn running on http://0.0.0.0:8000
```

Test the health endpoint:

```
curl https://your-app.ondigitalocean.app/health
```

## 5. Post-Deploy

- **Custom domain**: Settings -> Domains -> Add Domain
- **VPC networking**: Once databases are fully provisioned, switch to `private-` hostnames for lower latency
- **Scaling**: Increase `instance_count` in app spec if needed (keep single uvicorn process per instance)

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Build fails | Check Dockerfile builds locally: `docker build -t test .` |
| Health check fails | Verify `/health` endpoint returns 200. Check runtime logs |
| DB connection refused | Ensure database is Online and Trusted Sources includes your app |
| DB auth failure | Re-copy connection string from DO Console (passwords rotate) |
| Timeout on startup | Increase `initial_delay_seconds` in health check |

## Cost Estimate

- App Platform 1x 1vCPU/1GB: ~$12/mo
- PostgreSQL Basic: ~$15/mo
- Redis Basic: ~$15/mo
- **Total**: ~$42/mo
