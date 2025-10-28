# 🏒 NHL BETTING SYSTEM - QUICK REFERENCE CARD

## ⚡ DAILY WORKFLOW (5 MINUTES)

### **Morning (9 AM):**
```
Discord: !run
Wait 3 min
Discord: !edge
Place bets (10%+ edge)
```

### **Afternoon/Evening (Optional):**
```
Discord: !run    (lines update!)
Discord: !edge 15
```

### **Next Morning:**
```
Discord: !grade
```

---

## 💰 BET SIZING GUIDE

| Edge | Bet Size | Example ($1000) |
|------|----------|-----------------|
| 30%+ | 8-10% | $80-100 |
| 20-29% | 6-8% | $60-80 |
| 15-19% | 4-6% | $40-60 |
| 10-14% | 2-4% | $20-40 |
| 5-9% | Skip | $0 |

**Kelly Formula:** Kelly Score ÷ 4 = Bet %

---

## 🤖 DISCORD COMMANDS

| Command | Purpose |
|---------|---------|
| `!run` | Generate predictions & find edge (2-3 min) |
| `!edge` | Show 10%+ edge plays |
| `!edge 20` | Show 20%+ edge only |
| `!picks` | Show top predictions |
| `!grade` | Grade yesterday's results |
| `!stats` | Performance tracking |

---

## 📊 EMOJIS EXPLAINED

| Emoji | Name | Payout | Difficulty |
|-------|------|--------|------------|
| 🦝 | Goblin | 2.0x | Easy |
| ⚡ | Standard | 3.0x | Medium |
| 😈 | Demon | 4.0x | Hard |

**Goblin = Easier line, lower payout**
**Demon = Harder line, higher payout**

---

## 🎯 EDGE INTERPRETATION

```
+40% edge = MASSIVE (rare, bet big!)
+30% edge = HUGE (bet heavy)
+20% edge = STRONG (bet medium)
+10% edge = GOOD (bet small)
+5% edge = MARGINAL (skip)
```

**Rule:** Only bet 10%+ edge

---

## 📈 TARGETS

- **Hit Rate:** 60-65%
- **ROI:** 15-25%
- **T1-ELITE:** 70%+ accuracy
- **Bankroll Growth:** 20-30% monthly

---

## 🔧 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Bot responds twice | `taskkill /F /IM python.exe` then restart |
| No edge plays | Lines haven't updated, try later |
| Workflow warnings | Normal! Run `diagnose_workflow.py` |
| Unicode error | Already fixed in latest bot |

---

## 📁 KEY FILES

```
enhanced_predictions.py          → Generate predictions
prizepicks_integration_v2.py     → Find edge
run_automated_workflow.py        → Complete workflow
discord_bot_fixed.py             → Discord bot
grade_predictions.py             → Grade results
diagnose_workflow.py             → Troubleshoot
```

---

## 💡 PRO TIPS

1. **Run 2-3x daily** - Lines change!
2. **Focus on 15%+ edge** - Ignore 5-10%
3. **Diversify games** - Don't stack same game
4. **Track everything** - Spreadsheet is key
5. **Grade daily** - Improves model
6. **Trust the edge** - Ignore short-term variance

---

## 🚀 QUICK START

**First Time Setup:**
```bash
cd ~/PrizePicks-Research-Lab
python fix_id_column.py
python discord_bot_fixed.py
```

**Daily Use:**
```
Discord: !run
Discord: !edge
Place bets
Next day: !grade
```

**That's it!** 🎯

---

## 📞 HELP

**Workflow broken?**
```bash
python diagnose_workflow.py
```

**Bot issues?**
```bash
python check_bot_processes.py
```

**Need full guide?**
See `COMPLETE_SYSTEM_BOOKMARK.md`

---

**REMEMBER:**
- ✅ Only bet 10%+ edge
- ✅ Use Kelly sizing (÷4)
- ✅ Track every bet
- ✅ Grade daily
- ✅ Stay disciplined!

🏒💎🚀
