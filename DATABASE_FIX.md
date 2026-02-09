# Fixing PostgreSQL Authentication Error

## Problem
The application is failing to start with this error:
```
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "doadmin"
```

## Root Cause
The `DATABASE_URL` environment variable contains expired or incorrect credentials for your managed PostgreSQL database.

## Solution

### Step 1: Get the Correct DATABASE_URL

1. Log in to your [DigitalOcean Console](https://cloud.digitalocean.com/)
2. Navigate to **Databases** in the left sidebar
3. Click on your PostgreSQL database cluster
4. Go to the **Connection Details** tab
5. Select **Connection String** format
6. Copy the full connection string:
   ```
   postgresql://doadmin:PASSWORD@your-db-host.db.ondigitalocean.com:25060/defaultdb?sslmode=require
   ```

### Step 2: Update Environment Variable in App Platform

1. In DigitalOcean Console, navigate to **Apps**
2. Click on your application
3. Go to **Settings** tab
4. Find your backend service component
5. Click **Edit** next to Environment Variables
6. Find or add the `DATABASE_URL` variable
7. Paste the correct connection string from Step 1
8. Click **Save**
9. The app will automatically redeploy with the correct credentials

### Step 3: Verify the Fix

After the redeployment completes:
1. Check the **Runtime Logs** in your App Platform
2. You should see: `[Database] Using PostgreSQL: your-db-host...`
3. The app should start successfully without authentication errors

## Alternative: Reset Database Password

If you can't find the original password:

1. In DigitalOcean Console -> **Databases** -> Your PostgreSQL cluster
2. Go to **Users & Databases** tab
3. Click on the **doadmin** user
4. Click **Reset Password**
5. Copy the new password
6. Update your connection string with the new password
7. Update the `DATABASE_URL` in App Platform as described in Step 2

## Advanced Troubleshooting

### 1. Check for Special Characters in Password

If your password contains special characters like `!@#$%^&*`, they **must be URL-encoded** in the connection string:

| Character | URL Encoded |
|-----------|-------------|
| `!` | `%21` |
| `@` | `%40` |
| `#` | `%23` |
| `$` | `%24` |
| `%` | `%25` |
| `^` | `%5E` |
| `&` | `%26` |
| `*` | `%2A` |
| `/` | `%2F` |

**Example:**
```
# Original password: MyP@ss!word#123
# URL-encoded: MyP%40ss%21word%23123

# Correct connection string:
postgresql://doadmin:MyP%40ss%21word%23123@host:25060/defaultdb?sslmode=require
```

### 2. Verify Trusted Sources in DigitalOcean

Your database might have IP restrictions:

1. Go to DigitalOcean Console -> Databases -> Your Cluster
2. Click **Settings** tab
3. Look for **Trusted Sources**
4. Make sure your App Platform is in the trusted sources
5. If not, add it or temporarily allow all sources for testing

### 3. Check Database Status

Ensure your database is actually running:

1. DigitalOcean Console -> Databases -> Your Cluster
2. Check the **Status** at the top - should be "Online"
3. If it's not online, there may be maintenance or an issue

### 4. Force App Platform to Refresh Environment Variables

Sometimes App Platform caches old environment variables:

1. After updating DATABASE_URL, try **manually redeploying**:
   - Go to your App in DigitalOcean Console
   - Click **Actions** -> **Force Rebuild and Deploy**
2. Or add a dummy environment variable, save, remove it, and save again

### 5. Check App Platform Build vs Runtime Environment Variables

DigitalOcean has two types of environment variables:
- **Build-time** variables (used during build)
- **Run-time** variables (used when app is running)

Make sure DATABASE_URL is set as a **run-time** environment variable.

## Security Note

Never commit the actual `DATABASE_URL` with credentials to Git. Actual credentials should only be set in the DigitalOcean App Platform environment variables (marked as `type: SECRET`).
