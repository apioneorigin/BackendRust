# Fixing PostgreSQL Authentication Error

## Problem
The application is failing to start with this error:
```
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "doadmin"
```

## Root Cause
The `DATABASE_URL` environment variable in DigitalOcean App Platform contains expired or incorrect credentials for your managed PostgreSQL database.

## Solution

### Step 1: Get the Correct DATABASE_URL from DigitalOcean

1. Log in to your [DigitalOcean Console](https://cloud.digitalocean.com/)
2. Navigate to **Databases** in the left sidebar
3. Click on your PostgreSQL database cluster (should be named something like `db-postgresql-nyc1-24506`)
4. Go to the **Connection Details** tab
5. Select **Connection Parameters** dropdown
6. Choose **Connection String** format
7. Copy the full connection string that looks like:
   ```
   postgresql://doadmin:ACTUAL_PASSWORD_HERE@db-postgresql-nyc1-24506-do-user-33112092-0.m.db.ondigitalocean.com:25060/defaultdb?sslmode=require
   ```

### Step 2: Update Environment Variable in App Platform

1. In DigitalOcean Console, navigate to **Apps** in the left sidebar
2. Click on your application
3. Go to **Settings** tab
4. Find your web service component
5. Click **Edit** next to Environment Variables
6. Find or add the `DATABASE_URL` variable
7. Paste the correct connection string from Step 1
8. Click **Save**
9. The app will automatically redeploy with the correct credentials

### Step 3: Verify the Fix

After the redeployment completes:
1. Check the **Runtime Logs** in your App Platform
2. You should see: `[Database] Using PostgreSQL: db-postgresql-nyc1-24506-do-user-33112092-0.m.db.ondigitalocean.com`
3. The app should start successfully without authentication errors

## Alternative: Reset Database Password

If you can't find the original password:

1. In DigitalOcean Console → **Databases** → Your PostgreSQL cluster
2. Go to **Users & Databases** tab
3. Click on the **doadmin** user
4. Click **Reset Password**
5. Copy the new password
6. Update your connection string with the new password
7. Update the `DATABASE_URL` in App Platform as described in Step 2

## Advanced Troubleshooting

### If you've tried everything and it still fails:

#### 1. Test Connection Locally First

Run the diagnostic script to verify your DATABASE_URL works:

```bash
cd backend
python test_db_connection.py
```

This will:
- Parse your DATABASE_URL and show all components
- Detect special characters in the password that may need encoding
- Test the actual connection to DigitalOcean
- Show helpful error messages

#### 2. Check for Special Characters in Password

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

The diagnostic script will automatically detect and encode these for you.

#### 3. Verify Trusted Sources in DigitalOcean

Your database might have IP restrictions:

1. Go to DigitalOcean Console → Databases → Your Cluster
2. Click **Settings** tab
3. Look for **Trusted Sources**
4. Make sure your App Platform is in the trusted sources
5. If not, add it or temporarily allow all sources for testing

#### 4. Check Database Status

Ensure your database is actually running:

1. DigitalOcean Console → Databases → Your Cluster
2. Check the **Status** at the top - should be "Online"
3. If it's not online, there may be maintenance or an issue

#### 5. Force App Platform to Refresh Environment Variables

Sometimes App Platform caches old environment variables:

1. After updating DATABASE_URL, try **manually redeploying**:
   - Go to your App in DigitalOcean Console
   - Click **Actions** → **Force Rebuild and Deploy**
2. Or add a dummy environment variable, save, remove it, and save again

#### 6. Verify You're Using the Right Database

If you have multiple databases:

1. Check the logs to see which database it's trying to connect to:
   ```
   [Database] Received DATABASE_URL: postgresql://doadmin:***@db-postgresql-nyc1-XXXXX...
   ```
2. Compare the `XXXXX` number with your database cluster ID in DigitalOcean
3. Make sure you copied the connection string from the **correct** database

#### 7. Check App Platform Build vs Runtime Environment Variables

DigitalOcean has two types of environment variables:
- **Build-time** variables (used during build)
- **Run-time** variables (used when app is running)

Make sure DATABASE_URL is set as a **run-time** environment variable.

#### 8. Try Connection Pooling Settings

If the basic connection works but App Platform fails, try adjusting the connection pool:

In DigitalOcean → Databases → Your Cluster → **Connection Pools** tab:
1. Create a new connection pool
2. Mode: Session
3. Size: 10-25
4. Use the connection pool URL instead of direct database URL

## Security Note

Never commit the actual `DATABASE_URL` with credentials to Git. The `.env.digitalocean` file should remain with empty values, and actual credentials should only be set in the DigitalOcean App Platform environment variables.
