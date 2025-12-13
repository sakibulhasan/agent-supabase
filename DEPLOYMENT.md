# Deployment Guide: AI Supabase Agent to Render.com

## Prerequisites
- GitHub account with this repository
- Render.com account (sign up at https://render.com)
- Your environment variables ready:
  - SUPABASE_URL
  - SUPABASE_ANON_KEY
  - GEMINI_API_KEY
  - JWT_SECRET (optional)

---

## Step 1: Prepare Your Repository

### 1.1 Ensure all files are committed
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 1.2 Verify `render.yaml` exists
The `render.yaml` file has been created in your project root. This tells Render how to build and deploy your app.

---

## Step 2: Create Render Account and Connect GitHub

### 2.1 Sign up for Render
1. Go to https://render.com
2. Click "Get Started" or "Sign Up"
3. Choose "Sign up with GitHub" (recommended for automatic deployments)
4. Authorize Render to access your GitHub account

### 2.2 Install Render GitHub App (if needed)
1. Render will prompt you to install the Render GitHub App
2. Choose to install it on "All repositories" or "Only select repositories"
3. If selecting specific repos, choose `sakibulhasan/agent-supabase`
4. Click "Install"

---

## Step 3: Create a New Web Service

### 3.1 From Render Dashboard
1. Click "New +" button in the top right
2. Select "Web Service"

### 3.2 Connect Repository
1. You'll see a list of your GitHub repositories
2. Find `sakibulhasan/agent-supabase`
3. Click "Connect"

**Note:** If you don't see your repository:
- Click "Configure account" to grant access
- Or manually enter the repository URL

---

## Step 4: Configure Your Web Service

Render will auto-detect settings from `render.yaml`, but verify/configure:

### 4.1 Basic Settings
- **Name:** `ai-supabase-agent` (or your preferred name)
- **Region:** Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch:** `main`
- **Runtime:** Python 3

### 4.2 Build & Deploy Settings
These should be auto-filled from `render.yaml`:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 4.3 Instance Type
- **Plan:** Free (or choose Starter for better performance)
- Free tier includes:
  - 512 MB RAM
  - Shared CPU
  - Automatic sleep after 15 min of inactivity
  - Wake up on incoming request

---

## Step 5: Add Environment Variables

**CRITICAL:** Add your environment variables before deploying.

### 5.1 In the Render service configuration page:
1. Scroll to "Environment Variables" section
2. Click "Add Environment Variable" for each:

```
Key: SUPABASE_URL
Value: https://your-project.supabase.co

Key: SUPABASE_ANON_KEY
Value: your-supabase-anon-key-here

Key: GEMINI_API_KEY
Value: your-gemini-api-key-here

Key: JWT_SECRET
Value: your-jwt-secret-here (optional, but recommended)

Key: PYTHON_VERSION
Value: 3.11.1
```

### 5.2 Security Tips
- ✅ All values are automatically encrypted by Render
- ✅ Never commit `.env` file to GitHub (it's in `.gitignore`)
- ✅ Use strong, unique values for JWT_SECRET

---

## Step 6: Deploy Your Application

### 6.1 Initial Deployment
1. After adding environment variables, click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start your application
3. Monitor the deployment in the Logs tab

### 6.2 Deployment Process
You'll see logs showing:
```
==> Cloning from https://github.com/sakibulhasan/agent-supabase...
==> Installing dependencies...
==> Starting service with 'uvicorn main:app --host 0.0.0.0 --port $PORT'
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:10000
==> Your service is live 🎉
```

### 6.3 Get Your Live URL
- Once deployed, Render provides a URL like:
  - `https://ai-supabase-agent.onrender.com`
- This is your live API endpoint!

---

## Step 7: Verify Deployment

### 7.1 Test Health Endpoint
```bash
curl https://ai-supabase-agent.onrender.com/
```
Expected response: `{"status":"ok"}`

### 7.2 Test AI Agent
```bash
curl -X POST "https://ai-supabase-agent.onrender.com/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total income in 2024?"}'
```

---

## Step 8: Configure Automatic Deployments (Already Set Up!)

### 8.1 How It Works
✅ **Automatic deployments are already configured!**

When you push to the `main` branch:
1. GitHub sends a webhook to Render
2. Render automatically:
   - Pulls latest code
   - Rebuilds the application
   - Deploys the new version
   - Zero-downtime deployment

### 8.2 Manual Deployments (Optional)
You can also trigger manual deployments:
1. Go to your service in Render Dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

### 8.3 View Deployment History
- Check the "Events" tab in Render Dashboard
- See all deployments, when they happened, and their status

---

## Step 9: Custom Domain (Optional)

### 9.1 Add Custom Domain
1. In your service settings, go to "Custom Domains"
2. Click "Add Custom Domain"
3. Enter your domain (e.g., `api.yourdomain.com`)
4. Follow DNS configuration instructions

### 9.2 SSL Certificate
- Render automatically provisions and renews SSL certificates
- Your API will be available via HTTPS

---

## Step 10: Monitor Your Application

### 10.1 Available Monitoring
- **Logs:** Real-time application logs in the Dashboard
- **Metrics:** CPU, Memory usage (on paid plans)
- **Health Checks:** Automatic health monitoring

### 10.2 Set Up Notifications
1. Go to Settings → Notifications
2. Configure notifications for:
   - Deploy failures
   - Service crashes
   - Health check failures

---

## Common Issues and Solutions

### Issue 1: Build Fails
**Solution:** Check that `requirements.txt` is complete
```bash
# Test locally first
pip install -r requirements.txt
```

### Issue 2: Application Crashes on Startup
**Solution:** 
- Check environment variables are set correctly
- Review logs in Render Dashboard
- Ensure all required env vars are present

### Issue 3: Slow First Request (Free Tier)
**Solution:** 
- Free tier apps sleep after 15 minutes of inactivity
- First request takes ~30 seconds to wake up
- Upgrade to Starter plan for 24/7 availability

### Issue 4: Database Connection Errors
**Solution:**
- Verify SUPABASE_URL and SUPABASE_ANON_KEY are correct
- Check Supabase project is accessible
- Ensure `execute_sql` function is created (see `supabase_setup.sql`)

---

## Update CORS Settings (Important!)

After deployment, update `main.py` to allow your Render domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ai-supabase-agent.onrender.com",  # Add your Render URL
        "https://your-frontend-domain.com"         # Add your frontend domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push this change - it will auto-deploy!

---

## Quick Command Reference

### Push and Auto-Deploy
```bash
git add .
git commit -m "Your commit message"
git push origin main
# Render automatically deploys!
```

### View Logs
```bash
# In Render Dashboard → Your Service → Logs
# Or use Render CLI (optional)
render logs -f
```

### Rollback Deployment
```bash
# In Render Dashboard → Events → Click "Rollback" on any previous deploy
```

---

## Cost Considerations

### Free Tier (Perfect for testing)
- 750 hours/month free
- Multiple services allowed
- Sleeps after 15 min inactivity
- Shared CPU and 512 MB RAM

### Starter Plan ($7/month)
- Always-on (no sleeping)
- Dedicated resources
- Better performance
- Custom domains included

---

## Next Steps

1. ✅ Deploy to Render following steps above
2. ✅ Test your live API
3. ✅ Set up custom domain (optional)
4. ✅ Configure frontend to use new API URL
5. ✅ Monitor application health
6. ✅ Set up alerts for failures

---

## Support Resources

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **GitHub Issues:** Report issues in your repository
- **Status Page:** https://status.render.com

---

## Checklist

Before going to production:

- [ ] All environment variables configured
- [ ] Database function `execute_sql` created in Supabase
- [ ] CORS settings updated with production domains
- [ ] Tested all API endpoints
- [ ] Set up monitoring and alerts
- [ ] Documented API endpoints for your team
- [ ] Consider upgrading to paid plan for 24/7 availability

---

**Your AI Supabase Agent is now ready for production deployment! 🚀**
