# Quick Start: Deploy to Render.com

## 📋 Pre-Deployment Checklist

Have these ready:
- ✅ GitHub account
- ✅ Render.com account (free signup)
- ✅ Your Supabase URL
- ✅ Your Supabase Anon Key
- ✅ Your Gemini API Key

---

## 🚀 5-Minute Deployment Steps

### Step 1: Push Code to GitHub
```bash
cd /Users/sakibulhasan/code/adk/agent-supabase
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Sign Up & Connect to Render
1. Go to https://render.com
2. Click "Get Started" → "Sign up with GitHub"
3. Authorize Render to access your GitHub

### Step 3: Create Web Service
1. In Render Dashboard, click "New +" → "Web Service"
2. Find and click "Connect" on `agent-supabase` repository
3. Render will auto-detect settings from `render.yaml`

### Step 4: Add Environment Variables
Click "Add Environment Variable" for each:

```
SUPABASE_URL = https://blvrxmzvrjwtxhnfphuo.supabase.co
SUPABASE_ANON_KEY = your-anon-key-here
GEMINI_API_KEY = your-gemini-key-here
JWT_SECRET = your-random-secret-32-chars-minimum
```

### Step 5: Deploy!
1. Click "Create Web Service"
2. Wait 2-3 minutes for deployment
3. Your API will be live at: `https://your-app-name.onrender.com`

---

## ✅ Test Your Deployment

### Health Check
```bash
curl https://your-app-name.onrender.com/
# Response: {"status":"ok"}
```

### Test AI Agent
```bash
curl -X POST "https://your-app-name.onrender.com/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total income in 2024?"}'
```

---

## 🔄 Automatic Deployments (Already Configured!)

Every time you push to `main` branch:
```bash
git add .
git commit -m "Update feature"
git push origin main
# → Render automatically deploys! 🎉
```

No additional configuration needed!

---

## 📚 Full Documentation

See `DEPLOYMENT.md` for:
- Detailed step-by-step guide
- Troubleshooting tips
- Custom domain setup
- Monitoring and alerts
- Production best practices

---

## 💰 Free Tier Details

- ✅ 750 hours/month free
- ✅ Automatic HTTPS
- ✅ Automatic deployments
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ ~30 sec wake-up time on first request

**Upgrade to Starter ($7/mo) for 24/7 uptime**

---

## 🆘 Common Issues

**Build fails?**
- Check all dependencies in `requirements.txt`

**App crashes?**
- Verify environment variables are set
- Check logs in Render Dashboard

**Database errors?**
- Ensure Supabase credentials are correct
- Run `supabase_setup.sql` in Supabase SQL Editor

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- GitHub Issues: Create issue in your repository

---

**That's it! Your AI Supabase Agent is production-ready! 🚀**
