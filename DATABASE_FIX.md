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

## Security Note

Never commit the actual `DATABASE_URL` with credentials to Git. The `.env.digitalocean` file should remain with empty values, and actual credentials should only be set in the DigitalOcean App Platform environment variables.
