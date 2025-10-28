# 🤖 Discord Bot - Complete Setup & Usage Guide

## 🚀 Quick Start (10 minutes)

### **Step 1: Create Discord Bot**

1. Go to https://discord.com/developers/applications
2. Click **"New Application"**
3. Name it: `NHL Prediction Bot`
4. Click **"Create"**

### **Step 2: Configure Bot**

1. Go to **"Bot"** tab on left sidebar
2. Click **"Add Bot"** → Confirm
3. Under **"Privileged Gateway Intents"**:
   - ✅ Enable **"Message Content Intent"**
   - ✅ Enable **"Server Members Intent"**
4. Click **"Reset Token"** → **"Copy"** (save this token!)

### **Step 3: Invite Bot to Your Server**

1. Go to **"OAuth2"** → **"URL Generator"**
2. Select **Scopes:**
   - ✅ `bot`
3. Select **Bot Permissions:**
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Add Reactions
4. Copy the generated URL at bottom
5. Paste URL in browser → Select your server → **"Authorize"**

### **Step 4: Set Token in Windows**

**Option A: Set for current session:**
```powershell
$env:DISCORD_BOT_TOKEN="paste_your_token_here"
python discord_bot_enhanced.py
```

**Option B: Set permanently (recommended):**
```powershell
# 1. Open System Environment Variables
# Press Win+R → type: sysdm.cpl → Enter
# Go to "Advanced" tab → "Environment Variables"

# 2. Under "User variables" → Click "New"
# Variable name: DISCORD_BOT_TOKEN
# Variable value: paste_your_token_here

# 3. Click OK, restart PowerShell
python discord_bot_enhanced.py
```

**Option C: Create .env file (easiest for coding):**
```powershell
# Create a file called .env in your project root:
echo DISCORD_BOT_TOKEN=your_token_here > .env

# Then run:
python discord_bot_enhanced.py
```

---

## 🎮 Using the Bot

### **Available Commands:**

| Command | Description | Example |
|---------|-------------|---------|
| `!run` | Generate today's picks (full automation) | `!run` |
| `!picks` | Show top 15 picks for today | `!picks` |
| `!picks [date]` | Show picks for specific date | `!picks 2025-10-25` |
| `!optimizer` | Find best EV picks | `!optimizer` |
| `!dashboard` | Show performance stats | `!dashboard` |
| `!grade` | Grade yesterday's picks | `!grade` |
| `!grade [date]` | Grade specific date | `!grade 2025-10-24` |
| `!top` | Top 10 performing players | `!top` |
| `!help` | Show all commands | `!help` |

---

## 📅 Daily Workflow via Discord

### **Morning (Before Games):**

In your Discord server, type:
```
!run
```

Bot will:
1. ✅ Generate today's predictions
2. ✅ Compare with PrizePicks lines
3. ✅ Show top 5 picks instantly

Then:
```
!picks
```

Bot shows:
- 🔥 Top 5 T1-ELITE picks (detailed)
- ⭐ Top 3 T2-STRONG picks
- 📊 Summary stats

**Optional:**
```
!optimizer
```

Shows top 5 EV picks with demon/goblin lines

---

### **Next Morning (After Games):**

```
!grade
```

Bot grades yesterday automatically

Then:
```
!dashboard
```

Shows:
- Overall stats (hit rate, ROI, profit)
- Performance by tier
- Last 5 days results
- Status (🔥 Crushing it! / ✅ Profitable / etc.)

---

### **Anytime:**

```
!top
```

Shows top 10 performing players (helps you identify consistent winners)

---

## 💬 Example Discord Session

**User:** `!run`

**Bot:** 
```
🚀 Running Complete Automation...
⏳ This will take 2-3 minutes. Please wait...

✅ Automation Complete!

📊 Automation Summary
Successfully generated 46 predictions

🏆 Top 5 Picks
1. Kevin Fiala (LAK)
   └ SOG O3.5 | 75% | Kelly: 24.3

2. Quinn Hughes (VAN)
   └ SOG O3.5 | 75% | Kelly: 23.9

3. Kyle Connor (WPG)
   └ SOG O3.5 | 73% | Kelly: 22.5

4. Jake Guentzel (TBL)
   └ SOG O3.5 | 73% | Kelly: 22.3

5. Evan Bouchard (EDM)
   └ SOG O3.5 | 73% | Kelly: 21.6

💡 Use !picks to see all picks | !optimizer for best EV
```

---

**User:** `!optimizer`

**Bot:**
```
💎 Running EV optimizer for 2025-10-26...

✅ Optimizer complete!

💎 Top 5 EV Picks
1. Kevin Fiala (LAK) ⚡
   SOG O3.5
   75% prob | +341% EV | Kelly: 24.3

2. Quinn Hughes (VAN) 😈
   SOG O4.5
   68% prob | +428% EV | Kelly: 31.2

3. Kyle Connor (WPG) 🦝
   SOG O2.5
   82% prob | +289% EV | Kelly: 19.8

💡 Demon 😈 = harder line, higher payout | Goblin 🦝 = easier line
```

---

**Next Day:**

**User:** `!grade`

**Bot:**
```
📊 Grading predictions for 2025-10-25...

✅ Grading complete for 2025-10-25!
Use !dashboard to see updated stats.
```

**User:** `!dashboard`

**Bot:**
```
🏒 NHL Prediction System Dashboard
Overall performance statistics

📊 Overall Stats
Total Picks: 73
Hits: 46 ✅
Misses: 27 ❌
Hit Rate: 63.0%

💰 Profit & ROI
Profit: +14.86 units
ROI: +20.4%
Avg Prob: 67.2%

🎯 Performance by Tier
🔥 T1-ELITE: 26/37 (70.3%)
⭐ T2-STRONG: 15/24 (62.5%)
💎 T3-MARGINAL: 5/12 (41.7%)

📅 Last 5 Days
2025-10-25: 17/27 (63%) | +5.5u
2025-10-24: 12/19 (63%) | +3.9u
2025-10-23: 9/15 (60%) | +2.5u
2025-10-22: 5/8 (63%) | +1.6u
2025-10-21: 3/4 (75%) | +1.3u

Status: 🔥 CRUSHING IT!
```

---

## 🎯 Best Practices

### **For Solo Use:**
- Run `!run` every morning
- Review picks before betting
- Use `!grade` next morning to track performance
- Check `!dashboard` weekly

### **For Group/Server:**
- Create a dedicated `#nhl-picks` channel
- Pin bot commands with `!help`
- Share picks daily with `!picks`
- Discuss performance using `!dashboard`
- Compare notes with `!top` performers

### **For Automation:**
- Bot runs 24/7 once started
- Just send commands when needed
- Bot remembers nothing (stateless)
- All data stored in your local database

---

## 🔧 Troubleshooting

### **Bot won't start:**
```powershell
# Verify token is set:
echo $env:DISCORD_BOT_TOKEN

# Should show your token. If blank:
$env:DISCORD_BOT_TOKEN="your_token_here"
```

### **Bot offline in Discord:**
- Check bot process is running in PowerShell
- Press `Ctrl+C` to stop, then restart:
```powershell
python discord_bot_enhanced.py
```

### **Bot doesn't respond to commands:**
- Verify "Message Content Intent" is enabled in Discord Developer Portal
- Check bot has permissions in your server
- Try `!help` - if nothing, restart bot

### **Commands fail:**
- Make sure scripts exist in your project root:
  - `enhanced_predictions.py`
  - `optimize_ev.py`
  - `grade_predictions.py`
  - `complete_automation.py`
- Check database exists: `database/nhl_predictions.db`

### **"Automation failed" error:**
- Scripts may have errors
- Run manually to see full error:
```powershell
python complete_automation.py
```

---

## 🔒 Security Notes

**⚠️ NEVER share your bot token!**
- Token = full access to your bot
- If leaked, reset token in Discord Developer Portal
- Don't commit to GitHub (use `.gitignore`)

**Recommended .gitignore:**
```
.env
*.db
daily_picks.json
__pycache__/
```

---

## 🚀 Advanced Usage

### **Run bot in background (Windows):**

Create `start_bot.bat`:
```batch
@echo off
set DISCORD_BOT_TOKEN=your_token_here
python discord_bot_enhanced.py
pause
```

Double-click to run!

### **Auto-restart bot on crash:**

Create `bot_watcher.bat`:
```batch
@echo off
:loop
python discord_bot_enhanced.py
echo Bot crashed! Restarting in 5 seconds...
timeout /t 5
goto loop
```

### **Multiple servers:**
- Same bot can join multiple servers
- All servers share same picks/database
- Great for sharing with friends!

---

## 📊 What Bot Does NOT Do

- ❌ Place bets for you (you decide & bet manually)
- ❌ Store user data (stateless, uses local DB only)
- ❌ Work without local scripts (needs your system running)
- ❌ Auto-generate without command (you trigger with `!run`)

---

## 💡 Pro Tips

1. **Create channel permissions:**
   - Public `#nhl-picks` - anyone can view
   - Private `#nhl-admin` - only you can run `!run`

2. **Pin daily picks:**
   - Use Discord's pin feature on `!picks` output
   - Easy reference throughout the day

3. **Use reactions:**
   - 💰 = Bet placed
   - ✅ = Hit
   - ❌ = Miss
   - Track your personal picks!

4. **Share with friends:**
   - Invite bot to their servers
   - Everyone sees same picks
   - Track group performance

---

## 🎉 You're Ready!

**Start the bot:**
```powershell
$env:DISCORD_BOT_TOKEN="your_token_here"
python discord_bot_enhanced.py
```

**Then in Discord:**
```
!help
!run
!picks
```

**You now have a professional NHL picks bot!** 🏒💎

**Share picks, track performance, make money!** 💰🚀
