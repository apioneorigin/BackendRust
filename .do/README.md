# DigitalOcean App Platform Configuration

## ⚠️ Security Notice

**NEVER commit real API keys, passwords, or secrets to this repository!**

The `app.yaml` file is a template. All sensitive values must be set in the DigitalOcean Console UI.

## Setup Instructions

### 1. Rotate All Exposed Credentials

Your previous credentials were exposed and must be replaced:

```bash
# Generate new JWT secret
openssl rand -hex 32
```

Then get new keys from:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys

Reset database passwords:
- PostgreSQL: DO Console → Databases → Your cluster → Users & Databases → Reset Password
- Redis: DO Console → Databases → Your Redis cluster → Users → Reset Password

### 2. Update App Spec in DigitalOcean Console

1. Go to **DigitalOcean Console** → **Apps** → Your app
2. Click **Settings** → **App Spec**
3. Click **Edit**
4. Copy the contents of `.do/app.yaml` and paste it
5. Click **Save**

### 3. Set Secret Values in Console UI

1. Go to **Settings** → **Environment Variables**
2. Click **Edit**
3. For each SECRET variable, enter the actual value:
   - `OPENAI_API_KEY`: Your new OpenAI key
   - `ANTHROPIC_API_KEY`: Your new Anthropic key
   - `JWT_SECRET`: Generated JWT secret
   - `DATABASE_URL`: Connection string from DO (use PUBLIC hostname - without `private-`)
   - `REDIS_URL`: Connection string from DO (use PUBLIC hostname - without `private-`)
4. Click **Save**
5. The app will automatically redeploy

### 4. Get Database Connection Strings

#### PostgreSQL:
```
postgresql://doadmin:NEW_PASSWORD@db-postgresql-nyc1-13554-do-user-33112092-0.m.db.ondigitalocean.com:25060/defaultdb?sslmode=require
```

Get from: **Databases** → Your PostgreSQL cluster → **Connection Details** → Connection String

**Important:** Use the PUBLIC hostname (without `private-` prefix) until VPC networking is fully ready.

#### Redis:
```
rediss://default:NEW_PASSWORD@db-valkey-nyc1-33225-do-user-33112092-0.m.db.ondigitalocean.com:25061
```

Get from: **Databases** → Your Redis cluster → **Connection Details** → Connection String

### 5. Deploy

After setting all environment variables in the Console UI, the app will deploy automatically.

## Switching to VPC (Later)

Once your databases show connection details (not "provisioning"):

1. Change hostnames in environment variables from:
   - `db-postgresql-nyc1-13554...` → `private-db-postgresql-nyc1-13554...`
   - `db-valkey-nyc1-33225...` → `private-db-valkey-nyc1-33225...`
2. Redeploy
3. This gives you faster, more secure private network connections

## Security Checklist

- [ ] JWT_SECRET generated with `openssl rand -hex 32`
- [ ] All API keys rotated (new keys from providers)
- [ ] All database passwords reset
- [ ] Secrets set in DO Console UI only (not in YAML)
- [ ] `type: SECRET` added for all sensitive variables
- [ ] Public hostnames used (not `private-` until VPC ready)
- [ ] Previous exposed credentials revoked/deleted

## Support

If you encounter issues, see `../DATABASE_FIX.md` for troubleshooting.
