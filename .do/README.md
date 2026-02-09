# DigitalOcean App Platform

Two deployment specs are provided:

| File | What it deploys |
|------|----------------|
| `app.yaml` | Backend API only (FastAPI) |
| `app-fullstack.yaml` | Frontend (SvelteKit) + Backend (FastAPI) |

Choose the one that fits your setup. See `DEPLOY.md` (backend-only) or `DEPLOY-FULLSTACK.md` (full-stack) for step-by-step instructions.

## Prerequisites

Before deploying you need:

1. **DigitalOcean account** with App Platform access
2. **GitHub repo** connected to DO (`apioneorigin/BackendRust`)
3. **Managed PostgreSQL** database created in DO
4. **Managed Redis/Valkey** database created in DO (optional but recommended)
5. **API keys** for OpenAI and Anthropic

## Security

All secrets are declared as `type: SECRET` in the app specs. Set their actual values through the DO Console UI -- never commit real credentials to this repo.

Generate a JWT secret:

```bash
openssl rand -hex 32
```
