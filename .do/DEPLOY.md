# Deploy to DigitalOcean App Platform

## Quick Start - Create New App

### 1. Generate New JWT Secret

```bash
openssl rand -hex 32
```

Copy the output - you'll need it for step 3.

### 2. Get New API Keys

Get fresh API keys (revoke any exposed ones):
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys

### 3. Update app-with-credentials.yaml

Edit `.do/app-with-credentials.yaml` and replace these values:

```yaml
OPENAI_API_KEY: YOUR_NEW_OPENAI_KEY_HERE
ANTHROPIC_API_KEY: YOUR_NEW_ANTHROPIC_KEY_HERE
JWT_SECRET: YOUR_NEW_JWT_SECRET_HERE
```

**Database credentials are already set** with your new databases:
- PostgreSQL: `db-postgresql-nyc1-83404`
- Redis: `db-valkey-nyc1-88974`

### 4. Create App in DigitalOcean

1. Go to **DigitalOcean Console** → **Apps**
2. Click **Create App**
3. Choose **GitHub** as source
4. Select repository: `apioneorigin/BackendRust`
5. Select branch: `main`
6. Click **Next**
7. On the "Configure" screen, click **Edit App Spec**
8. Delete the auto-generated spec
9. Copy the ENTIRE contents of `.do/app-with-credentials.yaml`
10. Paste into the editor
11. Click **Save**
12. Review the configuration
13. Click **Next** → **Create Resources**

### 5. Wait for Deployment

The app will:
- ✅ Build from your Dockerfile
- ✅ Connect to PostgreSQL (public hostname)
- ✅ Connect to Redis (public hostname)
- ✅ Deploy to 2 instances (for high availability)

Check the **Runtime Logs** for:
```
[Database] Using PostgreSQL: db-postgresql-nyc1-83404...
Database initialized
✓ Application startup complete
```

### 6. Verify It's Working

Once deployed, visit your app URL and check:
- App loads successfully
- No timeout errors
- Database connections work

## Configuration Details

### Current Setup

- **PostgreSQL**: `db-postgresql-nyc1-83404` (Public hostname)
- **Redis**: `db-valkey-nyc1-88974` (Public hostname)
- **Instances**: 2x apps-s-1vcpu-1gb (1GB RAM, 1 vCPU each)
- **Region**: NYC1
- **Auto-deploy**: Enabled on `main` branch

### Why Public Hostnames?

Using public database hostnames (without `private-` prefix) ensures:
- ✅ No VPC timeout issues
- ✅ Immediate connectivity
- ✅ Works even if VPC isn't fully provisioned

You can switch to VPC private hostnames later for:
- Faster performance (< 1ms latency)
- Better security (private network)
- No bandwidth charges

### Switching to VPC Later

Once databases are fully provisioned (~30 minutes):

1. Update environment variables to use `private-` hostnames:
   ```
   postgresql://...@private-db-postgresql-nyc1-83404...
   rediss://...@private-db-valkey-nyc1-88974...
   ```
2. Save and redeploy
3. Verify connection in logs

## Troubleshooting

### If deployment fails:

1. **Check Runtime Logs**: Apps → Your app → Runtime Logs
2. **Look for errors**: Authentication, timeout, or connection errors
3. **Verify database status**: Databases → Check both are "Online"
4. **Check Trusted Sources**: Databases → Settings → Trusted Sources
   - Your app should be listed
   - Or set to "All sources" for testing

### Common Issues:

| Issue | Solution |
|-------|----------|
| Timeout errors | Databases still provisioning - wait 5-10 min |
| Auth failures | Double-check passwords in app spec |
| Connection refused | Check Trusted Sources settings |
| Build failures | Check Dockerfile and dependencies |

## Security Checklist

Before going live:

- [ ] New JWT_SECRET generated
- [ ] New OpenAI API key
- [ ] New Anthropic API key
- [ ] All old credentials revoked
- [ ] `app-with-credentials.yaml` NOT committed to git
- [ ] Environment variables set with `type: SECRET`
- [ ] Databases have Trusted Sources configured
- [ ] HTTPS enabled (automatic with DO App Platform)

## Cost Estimate

Current configuration:
- App Platform: 2x apps-s-1vcpu-1gb = ~$24/month
- PostgreSQL: Basic plan = ~$15/month
- Redis: Basic plan = ~$15/month
- **Total**: ~$54/month

## Next Steps After Deployment

1. ✅ Verify app is running
2. ✅ Test database connections
3. ✅ Monitor logs for errors
4. ⏳ Wait 30-60 min, then switch to VPC hostnames
5. 🔒 Set up custom domain with SSL
6. 📊 Configure monitoring and alerts

---

**Need help?** Check `README.md` or `DATABASE_FIX.md` for detailed troubleshooting.
