# Streamlit Cloud Deployment Guide

**Date:** November 2, 2025
**App:** NHL Prediction System Dashboard
**Status:** ✅ Ready for Deployment

---

## Prerequisites

✅ All met! Your app is ready to deploy.

- [x] `app.py` exists and works locally
- [x] `requirements.txt` complete
- [x] Database file exists (`database/nhl_predictions.db`)
- [x] All relative paths (no hard-coded absolute paths)
- [x] All schema issues fixed
- [x] Live scores working
- [x] Git repository (create if needed)

---

## Deployment Steps

### Step 1: Push to GitHub

If you haven't already, initialize git and push to GitHub:

```bash
# Navigate to your project
cd C:\Users\thoma\PrizePicks-Research-Lab

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Streamlit Cloud deployment - All fixes complete"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push
git push -u origin main
```

**Important:** Make sure these files are included:
- `app.py`
- `requirements.txt`
- `database/nhl_predictions.db`
- `.gitignore` (to exclude unnecessary files)

---

### Step 2: Create Streamlit Cloud Account

1. Go to **https://share.streamlit.io/**
2. Click **"Sign up"** or **"Sign in with GitHub"**
3. Authorize Streamlit to access your GitHub account

---

### Step 3: Deploy Your App

1. **Click "New app"** button

2. **Configure deployment:**
   - **Repository:** Select your GitHub repo
   - **Branch:** `main` (or your default branch)
   - **Main file path:** `app.py`

3. **Advanced settings (optional):**
   - **Python version:** 3.9+ (default is fine)
   - **Secrets:** None needed (no API keys in your app)

4. **Click "Deploy!"**

---

### Step 4: Wait for Deployment

Streamlit Cloud will:
1. Clone your repository ✅
2. Install dependencies from `requirements.txt` ✅
3. Start your app ✅

**Deployment time:** Usually 2-5 minutes

**You'll see logs like:**
```
Cloning repository...
Installing dependencies...
Building app...
App is live!
```

---

### Step 5: Access Your App

Once deployed, you'll get a URL like:
```
https://YOUR_USERNAME-YOUR_REPO_NAME-app-HASH.streamlit.app
```

**Your app is now live!** 🎉

You can:
- Share this URL with anyone
- Access from any device
- View predictions from anywhere

---

## Important Notes

### Database is Read-Only on Cloud

**What this means:**
- ✅ Dashboard works perfectly (viewing predictions, live scores, etc.)
- ❌ Cannot run prediction generation from cloud (Command Center buttons won't work)

**Why:**
Streamlit Cloud apps are ephemeral - any changes to files are lost when the app restarts.

**Solution:**
1. Generate predictions locally: `python RUN_DAILY_PICKS.py`
2. Push updated database to GitHub: `git push`
3. Streamlit Cloud auto-updates within minutes

---

## Auto-Update Workflow

To keep your cloud dashboard updated:

```bash
# 1. Generate fresh predictions locally
python RUN_DAILY_PICKS.py

# 2. Commit and push to GitHub
git add database/nhl_predictions.db
git commit -m "Update predictions for $(date +%Y-%m-%d)"
git push

# 3. Streamlit Cloud detects changes and redeploys (automatic)
```

**Streamlit Cloud will:**
- Detect the push within 1-2 minutes
- Pull latest code
- Restart app with new database

---

## Troubleshooting

### Issue: App shows "Module not found"

**Solution:** Check `requirements.txt` has all dependencies

Our file already has everything needed ✅

### Issue: Database not found

**Solution:** Make sure `database/nhl_predictions.db` is:
1. Committed to git
2. Pushed to GitHub
3. Not in `.gitignore`

Check your `.gitignore`:
```bash
# Make sure database is NOT ignored
# If you see this line, comment it out:
# database/*.db  <- Should be commented or removed
```

Our `.gitignore` already has this commented out ✅

### Issue: App is slow

**Solution:** Streamlit Cloud free tier has resource limits. Consider:
- Upgrading to paid tier for more resources
- Optimizing queries (already done ✅)
- Adding caching with `@st.cache_data` (optional enhancement)

### Issue: Live scores not updating

**Solution:** Click the "🔄 Refresh Scores" button

The app fetches live scores on demand (not continuously) to save resources.

---

## Updating Your App

### Code Changes

```bash
# Make changes to app.py
# Test locally: streamlit run app.py

# Commit and push
git add app.py
git commit -m "Update dashboard features"
git push

# Streamlit Cloud auto-redeploys
```

### Database Updates

```bash
# Generate new predictions
python RUN_DAILY_PICKS.py

# Push updated database
git add database/nhl_predictions.db
git commit -m "Daily predictions update"
git push

# Streamlit Cloud auto-updates
```

---

## GitHub Actions (Optional - Advanced)

To automate daily updates, create `.github/workflows/update-predictions.yml`:

```yaml
name: Update Predictions

on:
  schedule:
    - cron: '0 12 * * *'  # Run daily at noon UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate predictions
        run: python RUN_DAILY_PICKS.py

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add database/nhl_predictions.db
          git commit -m "Auto-update predictions $(date +%Y-%m-%d)" || exit 0
          git push
```

**This automatically:**
- Runs daily
- Generates fresh predictions
- Pushes to GitHub
- Triggers Streamlit Cloud redeployment

---

## What Will Work on Cloud

### ✅ Fully Functional

1. **📊 Command Center**
   - View top picks
   - See data freshness
   - View summary stats
   - ❌ Cannot run generators (buttons disabled or won't persist)

2. **🎯 Today's Predictions**
   - View all predictions
   - Filter by prop type
   - Filter by confidence tier
   - Search players
   - Download CSV

3. **💰 Edges & Parlays**
   - View edge opportunities
   - See GTO parlays
   - Filter by min EV

4. **📅 Schedule & Live Scores**
   - **View today's games** ✅
   - **Live scores with refresh** ✅
   - **Betting lines** ✅
   - All deduplication working ✅

5. **📈 Performance & Grading**
   - View performance metrics
   - See hit rates
   - View grading history
   - ❌ Auto-grading won't persist
   - ❌ Manual grading won't persist

### ❌ Won't Work (Requires Local)

- Running prediction generators
- Fetching new data
- Auto-grading predictions
- Manual grading
- Any database writes

**Solution:** Run these locally, push to GitHub

---

## Cost

**Free Tier:**
- 1 app
- Limited resources
- Auto-sleeps after inactivity
- Perfect for personal use ✅

**Paid Tier ($20/month):**
- More apps
- More resources
- No auto-sleep
- Custom domains

**Recommendation:** Start with free tier. Your app will work great!

---

## Security

**Good news:** Your app has no secrets!

- No API keys in code ✅
- No passwords ✅
- Database is public read-only ✅

**If you add API keys later:**
Use Streamlit Secrets:
1. Go to app settings on Streamlit Cloud
2. Add secrets in TOML format
3. Access with `st.secrets["key_name"]`

---

## Summary

### Ready to Deploy?

✅ Requirements complete
✅ Database included
✅ All fixes applied
✅ Live scores working
✅ Betting lines fixed

### Deployment Checklist

1. [ ] Push to GitHub
2. [ ] Go to share.streamlit.io
3. [ ] Connect GitHub account
4. [ ] Select repository
5. [ ] Set main file to `app.py`
6. [ ] Click Deploy
7. [ ] Wait 2-5 minutes
8. [ ] Share your URL!

### Daily Workflow

1. **Morning:** Generate predictions locally
   ```bash
   python RUN_DAILY_PICKS.py
   ```

2. **Push to GitHub:**
   ```bash
   git add database/nhl_predictions.db
   git commit -m "Daily update $(date +%Y-%m-%d)"
   git push
   ```

3. **Cloud auto-updates:** Within 1-2 minutes

4. **Access anywhere:** Your dashboard URL

---

## Need Help?

**Streamlit Docs:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app

**Your app is ready to go!** 🚀

---

**End of Guide**

Date: November 2, 2025
Status: ✅ Ready for Cloud Deployment
Next: Push to GitHub and deploy!
