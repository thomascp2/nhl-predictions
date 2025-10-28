# Discord Bot Setup Guide
## Fix "Improper token has been passed" Error

---

## Quick Setup (5 minutes)

### Step 1: Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Name it "NHL Predictions Bot"
4. Go to "Bot" tab (left sidebar)
5. Click "Add Bot"
6. Under "Token" section, click "Copy" (this is your bot token!)

### Step 2: Enable Required Permissions

Still on the Bot page:
1. Scroll down to "Privileged Gateway Intents"
2. Enable: "MESSAGE CONTENT INTENT"
3. Click "Save Changes"

### Step 3: Invite Bot to Your Server

1. Go to "OAuth2" → "URL Generator" (left sidebar)
2. Under "SCOPES", check:
   - `bot`
   - `applications.commands`
3. Under "BOT PERMISSIONS", check:
   - Send Messages
   - Read Messages/View Channels
   - Attach Files
   - Embed Links
4. Copy the generated URL at the bottom
5. Paste in browser, select your server, authorize

### Step 4: Add Token to Your Code

**Option 1: .env file (Recommended)**

Create `.env` file in `PrizePicks-Research-Lab/`:

```
DISCORD_BOT_TOKEN=paste_your_token_here
```

**Option 2: Direct in code (Quick test)**

Open `discord_bot.py`, find the bottom:

```python
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')

    if not token:
        # Add this line with your token:
        token = "YOUR_TOKEN_HERE"
```

### Step 5: Run Bot

```bash
python discord_bot.py
```

Should see:
```
[OK] Bot connected as NHL Predictions Bot#1234
```

### Step 6: Test in Discord

In your Discord server:
```
!commands
!generate
!picks T1-ELITE
```

---

## Security Notes

- **Never share your bot token!**
- Don't commit `.env` to GitHub
- Regenerate token if exposed

---

## Troubleshooting

**Bot offline?**
- Make sure `python discord_bot.py` is running
- Bot goes offline when script stops

**Commands not working?**
- Check bot has permissions in channel
- Verify "MESSAGE CONTENT INTENT" is enabled

**Want bot to run 24/7?**
- See hosting options below (or keep reading for better alternatives!)
