# NHL Prediction System - Full Automation Setup

**Date:** November 2, 2025
**Status:** ✅ READY FOR AUTOMATED OPERATION

---

## 🎯 What's Automated

### 1. Daily Predictions (4x per day)
- **7:00 AM** - Morning predictions
- **12:00 PM** - Midday refresh
- **3:00 PM** - Afternoon refresh
- **6:00 PM** - Evening refresh (game time!)

### 2. Auto-Grading (Every night)
- **11:00 PM** - Grades yesterday's predictions automatically

### 3. GitHub Integration (Automatic)
- Predictions auto-push to GitHub after every run
- View on mobile: [LATEST_PICKS.txt](https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt)

---

## 📱 Mobile Workflow (GitHub)

**Your new workflow is SIMPLE:**

1. Task Scheduler runs automatically 4x per day
2. Predictions generate and push to GitHub
3. Check picks on your phone: `https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt`
4. Done!

**No manual intervention needed!**

---

## ⚙️ Task Scheduler Setup

### Current Tasks (Need Update)

Your Task Scheduler currently has 4 NHL tasks running the OLD script:
- Task #6: NHL Morning Run 0700 → `run_complete_workflow_gto.py` ❌
- Task #7: NHL Picks Auto 1200 → `run_complete_workflow_gto.py` ❌
- Task #8: NHL Picks Auto 1500 → `run_complete_workflow_gto.py` ❌
- Task #9: NHL Picks Auto 1800 → `run_complete_workflow_gto.py` ❌
- Task #5: NHL Adaptive Learning 2300 → `grade_predictions.py` ✅ (correct)

### Update Task Scheduler (One-Time Setup)

**STEP 1: Run the updater (as Administrator)**
```bash
# Right-click and "Run as Administrator"
update_task_scheduler.bat
```

This will:
1. Delete old tasks
2. Create 5 new tasks with correct scripts:
   - 7 AM → RUN_DAILY_PICKS.py
   - 12 PM → RUN_DAILY_PICKS.py
   - 3 PM → RUN_DAILY_PICKS.py
   - 6 PM → RUN_DAILY_PICKS.py
   - 11 PM → auto_grade_predictions.py

**STEP 2: Verify setup**
```bash
python check_scheduled_tasks.py
```

All tasks should show status "Ready" ✅

---

## 🔄 What Happens Automatically

### Every Prediction Run (4x daily)

```
1. Smart Data Refresh
   ├─ Check if data is stale (>2 hours old)
   ├─ Fetch fresh stats if needed
   └─ Skip if data is fresh

2. Generate Predictions
   ├─ Run statistical model
   ├─ Run ensemble model
   └─ Run goalie saves model

3. Create Picks Files
   ├─ LATEST_PICKS.txt (mobile-friendly)
   ├─ LATEST_PICKS.csv (spreadsheet)
   ├─ PICKS_[timestamp].txt (backup)
   └─ PICKS_[timestamp].csv (backup)

4. GitHub Push (Automatic!)
   ├─ git add (all pick files)
   ├─ git commit -m "Auto-update..."
   └─ git push

5. Archive Old Picks
   └─ Move old timestamped files to archive/
```

### Every Night at 11 PM

```
1. Auto-Grade Yesterday's Predictions
   ├─ Fetch actual stats from NHL API
   ├─ Compare vs predictions
   ├─ Record HIT/MISS outcomes
   └─ Save to prediction_outcomes table

2. Ready for Learning Engine
   └─ Once 30+ graded, can run learning engine
```

---

## 📊 File Structure

### Generated Files (On GitHub)

**Always Up-to-Date:**
- `LATEST_PICKS.txt` ← Check this on mobile!
- `LATEST_PICKS.csv` ← Import to Excel

**Timestamped Backups:**
- `PICKS_2025-11-02_04-04PM.txt`
- `PICKS_2025-11-02_04-04PM.csv`
- `GTO_PARLAYS_2025-11-02_02-13PM.csv`
- `MULTI_LINE_EDGES_2025-11-02_02-13PM.csv`

**Archived (Local Only):**
- `archive/old_picks/` (old timestamped files)

---

## 📱 Viewing Picks on Mobile

### Option 1: GitHub (Recommended)
1. Open browser on phone
2. Go to: `https://github.com/thomascp2/nhl-predictions`
3. Click `LATEST_PICKS.txt`
4. View your top picks!

### Option 2: GitHub Mobile App
1. Install GitHub app
2. Open repository
3. Navigate to `LATEST_PICKS.txt`
4. Enable notifications for commits (optional)

### Option 3: Streamlit Cloud Dashboard
If you deployed to Streamlit Cloud:
- `https://[your-app-url].streamlit.app`
- Navigate to "Today's Predictions" tab

---

## 🎮 Manual Control (Optional)

If you want to generate picks manually:

**Generate Picks:**
```bash
python RUN_DAILY_PICKS.py
```

**Find Edges & Parlays:**
```bash
python RUN_EDGE_FINDER.py
```

**Grade Yesterday:**
```bash
python adaptive_learning\auto_grade_predictions.py
```

**View Dashboard:**
```bash
streamlit run app.py
```

---

## 🔧 Troubleshooting

### Issue: Picks not updating on GitHub

**Check:**
```bash
# Verify Git is working
git status

# Check last commit
git log -1

# Manual push if needed
git push origin main
```

### Issue: Task Scheduler not running

**Check:**
```bash
# View task status
python check_scheduled_tasks.py

# Run task manually
schtasks /run /tn "NHL Picks Auto 1200"
```

### Issue: No T1-ELITE picks

This is normal! It means:
- Confidence thresholds filtered all picks
- Try checking T2-STRONG or T3-SOLID in dashboard
- Or lower min_ev threshold in scripts

### Issue: Data is stale

**Manually refresh:**
```bash
python smart_data_refresh.py
```

---

## 📈 What's Next

### After 30+ Graded Predictions

Once you have 30+ graded predictions, you can run the learning engine to discover patterns:

```bash
python adaptive_learning/learning_engine.py
```

This analyzes:
- Which prediction types are most accurate
- Which players are most predictable
- Which situations have best hit rates
- Optimal confidence thresholds

### Future Enhancements

- **Discord bot** (sends picks to your phone)
- **Email notifications** (daily picks digest)
- **Telegram bot** (instant pick alerts)
- **Performance tracking** (automated ROI reporting)

---

## 🎯 Current Status

### ✅ Working Automatically
- Prediction generation (4x daily)
- GitHub auto-push
- Smart data refresh
- Archive old picks
- Mobile-friendly TXT format

### ⚠️ Needs One-Time Setup
- Task Scheduler update (run `update_task_scheduler.bat` as Admin)

### 🔄 Coming Soon
- Auto-grading at 11 PM (after Task Scheduler update)
- Learning engine insights
- Performance reports

---

## 📞 Quick Reference

**View Picks (Mobile):**
```
https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt
```

**Update Task Scheduler:**
```bash
# Right-click → Run as Administrator
update_task_scheduler.bat
```

**Manual Generation:**
```bash
python RUN_DAILY_PICKS.py
```

**Check Status:**
```bash
python check_scheduled_tasks.py
```

**Dashboard:**
```bash
streamlit run app.py
```

---

## 🎉 You're Done!

Your NHL prediction system is now:
- ✅ Fully automated
- ✅ Runs 4x per day
- ✅ Auto-pushes to GitHub
- ✅ Mobile-friendly
- ✅ Self-maintaining

**Just run `update_task_scheduler.bat` once as Administrator and you're set!**

Check GitHub on your phone for picks. That's it!

---

**Last Updated:** November 2, 2025
**System Version:** v2.0 (Fully Automated)
