# 🖥️ NHL Prediction System - Ultimate GUI Specification

**Status:** READY TO BUILD | **Estimated Time:** 5 hours | **Priority:** HIGH

---

## 📋 PROJECT OVERVIEW

### **Goal:**
Build a professional, interactive dashboard to replace command-line workflow with beautiful GUI.

### **Technology:**
- **Streamlit** (web-based, runs locally)
- **Plotly** (interactive charts)
- **Pandas** (data manipulation)
- **SQLite** (existing database)

### **Why Streamlit?**
✅ Fast to build (5 hours total)
✅ Beautiful by default
✅ Runs in browser (no complex setup)
✅ Real-time updates
✅ Interactive components
✅ Easy to maintain

---

## 🎨 ULTIMATE VERSION - FULL FEATURE SET

### **6 Main Pages:**

1. 🏠 **HOME** - Dashboard overview
2. 💎 **OPTIMIZER** - Best EV picks finder
3. 🎯 **TODAY'S PICKS** - Current predictions
4. 📊 **PERFORMANCE** - Analytics & charts
5. 📅 **GRADING** - Results review
6. ⚙️ **SETTINGS** - Configuration

---

## 📄 PAGE 1: HOME DASHBOARD

### **Layout:**
```
┌─────────────────────────────────────────┐
│  🏒 NHL PREDICTION SYSTEM v2.0          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│  📊 QUICK STATS          🎯 TODAY       │
│  ┌────────────────┐      ┌────────────┐ │
│  │ Hit Rate: 63%  │      │ Picks: 82  │ │
│  │ ROI: +20.3%    │      │ Games: 13  │ │
│  │ Profit: +16.4u │      │ T1: 47     │ │
│  └────────────────┘      └────────────┘ │
│                                          │
│  📈 30-DAY PROFIT CURVE                 │
│  [Plotly Line Chart]                    │
│                                          │
│  🏆 TOP 5 PICKS TODAY                   │
│  [Interactive Table - Click to expand]  │
│                                          │
│  ⚡ QUICK ACTIONS                        │
│  [Generate] [Grade] [Optimize] [Export]│
└─────────────────────────────────────────┘
```

### **Components:**
- **Stats Cards:** Real-time metrics with trend arrows
- **Profit Chart:** Plotly line chart (interactive, zoomable)
- **Top Picks Table:** Sortable, filterable, clickable rows
- **Quick Action Buttons:** One-click operations
- **Live Status:** Last update time, games today, etc.

### **Data Sources:**
```python
# Query database for stats
SELECT COUNT(*), SUM(CASE WHEN result='HIT'...) FROM predictions

# Today's picks
SELECT * FROM predictions WHERE game_date = today ORDER BY kelly_score DESC LIMIT 5

# Profit curve
SELECT game_date, SUM(profit) FROM predictions GROUP BY game_date
```

---

## 💎 PAGE 2: EV OPTIMIZER

### **Layout:**
```
┌─────────────────────────────────────────┐
│  💎 EV OPTIMIZER                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│  🔍 FILTERS                              │
│  [T1 ✓] [T2 ✓] [T3 ✗] | Min EV: [5%]  │
│  [Demon ✓] [Goblin ✓] [Standard ✓]    │
│                                          │
│  📊 OPTIMAL PICKS (43 found)            │
│  ┌────────────────────────────────────┐ │
│  │Rank│Player│Prop│Odds│Prob│EV│Kelly││
│  ├────────────────────────────────────┤ │
│  │ 1  │Pastrnak│PTS O1.5 😈│92%│+107%││
│  │ 2  │Sanderson│SOG O2.5 😈│85%│+92%││
│  │ ... (scrollable, sortable)         │ │
│  └────────────────────────────────────┘ │
│                                          │
│  📊 EV DISTRIBUTION                     │
│  [Histogram: EV ranges]                 │
│                                          │
│  💰 SUGGESTED PARLAYS (Top 5)          │
│  [Table: 2-leg parlays with combined EV]│
│                                          │
│  [Export CSV] [Copy All] [Refresh]     │
└─────────────────────────────────────────┘
```

### **Features:**
- **Real-time Filtering:** Instant updates as you change filters
- **Sortable Columns:** Click headers to sort
- **Row Selection:** Check boxes to build bet slip
- **Odds Type Indicators:** Emoji badges (😈 🦝 ⚡)
- **EV Histogram:** Visual distribution of value
- **Parlay Suggestions:** Auto-generated optimal combos
- **Export Options:** CSV, clipboard, print

### **Data Flow:**
```python
# Run optimizer
python optimize_ev.py → optimal_picks.json

# Load in GUI
df = pd.read_json('optimal_picks.json')

# Apply filters
filtered = df[df['ev'] > min_ev_slider]

# Display
st.dataframe(filtered, use_container_width=True)
```

---

## 🎯 PAGE 3: TODAY'S PICKS

### **Layout:**
```
┌─────────────────────────────────────────┐
│  🎯 TODAY'S PICKS - 2025-10-25          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│  View: [All] [T1] [T2] [Favorites]      │
│  Sort: [Kelly ▼] [Prob] [EV]            │
│  Search: [____________] 🔍              │
│                                          │
│  BET SLIP (2 selected)                  │
│  Total Risk: $100 | Expected: +$87      │
│  [Clear] [Export] [Mark Placed]         │
│                                          │
│  PICKS (82 total)                       │
│  ┌────────────────────────────────────┐ │
│  │[✓] David Pastrnak (BOS) vs COL    │ │
│  │    Points OVER 1.5 [DEMON] 😈     │ │
│  │    ┌─────────────────────────────┐│ │
│  │    │Prob: 92.3% | EV: +107.6%   ││ │
│  │    │Kelly: 21.5% → Bet $54      ││ │
│  │    │Reasoning: Elite scorer...  ││ │
│  │    └─────────────────────────────┘│ │
│  │                                    │ │
│  │[✓] Jake Sanderson (OTT) vs WSH   │ │
│  │    Shots OVER 2.5 [DEMON] 😈      │ │
│  │    [Expandable details...]         │ │
│  └────────────────────────────────────┘ │
│                                          │
│  [Select All T1] [Deselect All]         │
└─────────────────────────────────────────┘
```

### **Features:**
- **Expandable Cards:** Click to see full details
- **Checkboxes:** Build custom bet slip
- **Live Calculator:** Auto-calculate risk/reward
- **Favorites:** Star picks to save for later
- **Quick Filters:** One-click tier/prop filtering
- **Search Bar:** Find specific players
- **Bet Slip:** Selected picks summary
- **Export Slip:** Generate betting slip image

### **Interactive Elements:**
```python
# Checkbox selection
selected = st.multiselect("Select picks", picks_df['player'])

# Expandable details
with st.expander(f"{player} - {prop}"):
    st.metric("Probability", f"{prob:.1%}")
    st.metric("EV", f"+{ev:.1%}")
    st.text(reasoning)

# Bet slip calculator
total_risk = sum(kelly_amounts[selected])
expected_profit = sum(ev_amounts[selected])
st.metric("Total Risk", f"${total_risk}")
st.metric("Expected Profit", f"+${expected_profit}")
```

---

## 📊 PAGE 4: PERFORMANCE ANALYTICS

### **Layout:**
```
┌─────────────────────────────────────────┐
│  📊 PERFORMANCE ANALYTICS                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│  📅 Date Range: [Last 30 Days ▼]        │
│     Custom: [Start] [End] [Apply]       │
│                                          │
│  OVERVIEW METRICS                        │
│  ┌──────┬──────┬──────┬──────┐         │
│  │Picks │Hit % │ ROI  │Profit│         │
│  │ 169  │ 63%  │+20%  │+16.4u│         │
│  │▲ 87  │▲ 5%  │▲12%  │▲16.4u│         │
│  └──────┴──────┴──────┴──────┘         │
│                                          │
│  📈 PROFIT OVER TIME                    │
│  [Plotly Line Chart - cumulative]       │
│                                          │
│  🎯 PERFORMANCE BY TIER                 │
│  [Bar Chart: T1 64.3%, T2 50%, T3 71%] │
│                                          │
│  🏒 PERFORMANCE BY PROP TYPE            │
│  [Pie Chart: Points 71%, Shots 54%]    │
│                                          │
│  📅 CALENDAR HEATMAP                    │
│  [30-day grid colored by daily profit]  │
│                                          │
│  ⭐ TOP PLAYERS (min 3 picks)           │
│  [Sortable table with hit rates]        │
│                                          │
│  [Export Report] [Download Charts]      │
└─────────────────────────────────────────┘
```

### **Charts:**
1. **Profit Curve:** Cumulative profit over time
2. **Tier Performance:** Bar chart comparison
3. **Prop Type:** Pie chart breakdown
4. **Calendar Heatmap:** Daily profit grid
5. **Player Rankings:** Best/worst performers
6. **ROI Distribution:** Histogram of returns

### **Code Structure:**
```python
import plotly.express as px
import plotly.graph_objects as go

# Profit curve
fig = px.line(df, x='date', y='cumulative_profit')
st.plotly_chart(fig, use_container_width=True)

# Tier bar chart
fig = px.bar(tier_df, x='tier', y='hit_rate', color='tier')
st.plotly_chart(fig)

# Calendar heatmap
fig = go.Figure(data=go.Heatmap(
    z=profit_grid,
    colorscale='RdYlGn'
))
st.plotly_chart(fig)
```

---

## 📅 PAGE 5: GRADING & RESULTS

### **Layout:**
```
┌─────────────────────────────────────────┐
│  📅 GRADING & RESULTS                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│  📆 Select Date: [2025-10-24 ▼]         │
│                                          │
│  STATUS: ✅ Graded (81/87)              │
│  [Auto-Grade] [Manual Grade] [Re-Grade] │
│                                          │
│  SUMMARY                                 │
│  ┌────────────────────────────────────┐ │
│  │ Hits: 51 | Misses: 30 | Pending: 6 │ │
│  │ Hit Rate: 63.0% | Profit: +16.41u  │ │
│  │ ROI: +20.3%                         │ │
│  └────────────────────────────────────┘ │
│                                          │
│  FILTERS: [All] [Hits] [Misses] [Pending]│
│                                          │
│  RESULTS                                 │
│  ┌────────────────────────────────────┐ │
│  │✅ Werenski SOG O3.5 → 4 (86.8%)   │ │
│  │✅ Connor SOG O3.5 → 5 (73.3%)     │ │
│  │❌ Pastrnak SOG O3.5 → 3 (74.4%)   │ │
│  │✅ Kempe PTS O0.5 → 1 (62.1%)      │ │
│  │... (scrollable list)               │ │
│  └────────────────────────────────────┘ │
│                                          │
│  [Export Results] [View Details]        │
└─────────────────────────────────────────┘
```

### **Features:**
- **Date Picker:** Select any historical date
- **Auto-Grade Button:** One-click grading
- **Result Filters:** Show only hits/misses/pending
- **Color Coding:** Green ✅ hits, red ❌ misses
- **Quick Stats:** Summary cards
- **Export:** Generate PDF report
- **Re-Grade:** Fix incorrect grades

### **Grading Flow:**
```python
# Auto-grade button
if st.button("Auto-Grade"):
    with st.spinner("Grading..."):
        subprocess.run(["python", "grade_predictions_fixed.py", date])
    st.success("Grading complete!")
    st.rerun()

# Display results
results_df = pd.read_sql(f"SELECT * FROM predictions WHERE game_date = '{date}'", conn)

# Color code
def color_result(val):
    if val == 'HIT':
        return 'background-color: green'
    elif val == 'MISS':
        return 'background-color: red'
    return ''

st.dataframe(results_df.style.applymap(color_result))
```

---

## ⚙️ PAGE 6: SETTINGS

### **Layout:**
```
┌─────────────────────────────────────────┐
│  ⚙️ SETTINGS & CONFIGURATION            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│  💰 BANKROLL MANAGEMENT                 │
│  ├─ Total Bankroll: [$1000]            │
│  ├─ Kelly Fraction: [1/4 ▼]            │
│  ├─ Max Daily Risk: [30%]              │
│  └─ Unit Size: [Auto-calculate ✓]      │
│                                          │
│  🎯 PICK FILTERS                        │
│  ├─ Min Probability: [55%] slider      │
│  ├─ Min Kelly Score: [5] slider        │
│  ├─ Min EV: [5%] slider                │
│  ├─ Include T3-MARGINAL: [✗]           │
│  └─ Auto-exclude bad performers: [✓]   │
│                                          │
│  🔔 NOTIFICATIONS                       │
│  ├─ Desktop alerts: [✓]                │
│  ├─ Sound on new picks: [✓]            │
│  ├─ Email daily summary: [✗]           │
│  └─ Discord webhook: [Add URL]         │
│                                          │
│  🎨 APPEARANCE                          │
│  ├─ Theme: [Dark ● Light ○]            │
│  ├─ Chart colors: [Default ▼]          │
│  └─ Compact mode: [✗]                  │
│                                          │
│  🗄️ DATABASE                            │
│  ├─ Path: database/nhl_predictions.db  │
│  ├─ Size: 2.4 MB                        │
│  ├─ Records: 169                        │
│  └─ [Backup] [Optimize] [Reset]        │
│                                          │
│  📊 DATA SOURCES                        │
│  ├─ NHL API: [✓ Connected]             │
│  ├─ PrizePicks: [✓ Connected]          │
│  └─ [Test Connections]                  │
│                                          │
│  [Save Settings] [Reset Defaults]       │
└─────────────────────────────────────────┘
```

### **Persistent Storage:**
```python
import json

# Save settings
settings = {
    'bankroll': bankroll_input,
    'kelly_fraction': kelly_slider,
    'min_prob': min_prob_slider,
    # ...
}

with open('settings.json', 'w') as f:
    json.dump(settings, f)

# Load on startup
with open('settings.json', 'r') as f:
    settings = json.load(f)
```

---

## 🎨 ADVANCED FEATURES

### **1. Bet Slip Builder**
- Drag-and-drop picks
- Auto-calculate parlays
- Track placed bets
- Compare to actual results

### **2. Parlay Optimizer**
- Generate optimal 2-5 leg parlays
- Filter by combined probability
- Show expected value
- Avoid correlated props

### **3. Live Odds Tracker**
- Monitor line movement
- Alert on value changes
- Compare across sportsbooks
- Historical odds data

### **4. Player Deep Dive**
- Individual player analytics
- Matchup history
- Trend analysis
- Performance splits (home/away)

### **5. Correlation Matrix**
- Find related props
- Avoid correlated parlays
- Discover value stacks
- Heatmap visualization

### **6. Alerts & Notifications**
- Desktop notifications
- Sound alerts
- Email summaries
- Discord webhooks
- Custom triggers

### **7. Mobile Responsive**
- Works on phone/tablet
- Touch-friendly buttons
- Swipe gestures
- Offline mode

### **8. Export Everything**
- PDF reports
- CSV data
- Screenshots
- Print-friendly views
- Email integration

---

## 💻 TECHNICAL IMPLEMENTATION

### **File Structure:**
```
PrizePicks-Research-Lab/
├── app.py                    # Main Streamlit app
├── pages/
│   ├── 1_🏠_Home.py
│   ├── 2_💎_Optimizer.py
│   ├── 3_🎯_Todays_Picks.py
│   ├── 4_📊_Performance.py
│   ├── 5_📅_Grading.py
│   └── 6_⚙️_Settings.py
├── utils/
│   ├── database.py          # DB queries
│   ├── charts.py            # Plotly charts
│   ├── calculations.py      # Kelly, EV, etc.
│   └── export.py            # Export functions
├── assets/
│   ├── logo.png
│   └── styles.css
└── config/
    └── settings.json
```

### **Core Libraries:**
```python
streamlit==1.28.0
plotly==5.17.0
pandas==2.1.0
numpy==1.25.0
sqlite3 (built-in)
```

### **Installation:**
```powershell
pip install streamlit plotly pandas numpy
```

### **Launch:**
```powershell
streamlit run app.py
```

Opens in browser at `http://localhost:8501`

---

## 🎯 DEVELOPMENT PHASES

### **Phase 1: Core (2 hours)**
✅ Home dashboard
✅ Basic tables
✅ Simple charts
✅ Database connection

### **Phase 2: Features (2 hours)**
✅ EV optimizer page
✅ Grading interface
✅ Performance charts
✅ Export functions

### **Phase 3: Polish (1 hour)**
✅ Dark mode
✅ Animations
✅ Notifications
✅ Mobile responsive
✅ Error handling

---

## 📝 IMPLEMENTATION NOTES

### **Session State:**
Use Streamlit session state for:
- Selected picks
- Filter settings
- User preferences
- Bet slip

```python
if 'selected_picks' not in st.session_state:
    st.session_state.selected_picks = []
```

### **Caching:**
Cache expensive operations:
```python
@st.cache_data
def load_predictions(date):
    return pd.read_sql(query, conn)
```

### **Real-time Updates:**
Use `st.rerun()` to refresh on changes:
```python
if st.button("Generate Picks"):
    subprocess.run(["python", "enhanced_predictions.py"])
    st.rerun()
```

### **Styling:**
Custom CSS for polish:
```python
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)
```

---

## 🚀 NEXT SESSION ACTION PLAN

### **What to do:**

1. **Start fresh session**
2. **Say:** "Build the Ultimate GUI for NHL Prediction System - see GUI_SPEC.md"
3. **I'll create all 6 pages** with full functionality
4. **You test and provide feedback**
5. **I polish and add advanced features**

### **Estimated Timeline:**
- Hour 1: Core pages (Home, Picks, Performance)
- Hour 2: Optimizer & Grading pages
- Hour 3: Settings & advanced features
- Hour 4: Charts, exports, notifications
- Hour 5: Polish, testing, deployment

---

## 🎉 END RESULT

You'll have a **professional, beautiful dashboard** that:
- ✅ Replaces all command-line tools
- ✅ Runs locally in browser
- ✅ Real-time updates
- ✅ Interactive charts
- ✅ One-click workflows
- ✅ Export everything
- ✅ Mobile-friendly
- ✅ Dark/Light themes

**You'll go from this:**
```powershell
python optimize_ev.py
python grade_predictions_fixed.py
python dashboard_fixed.py
```

**To this:**
```powershell
streamlit run app.py
[Beautiful GUI opens in browser]
[Click buttons, see charts, make money]
```

---

## 💾 FILES TO REFERENCE NEXT SESSION

When building, use these existing files:
- `database/nhl_predictions.db` (data source)
- `optimize_ev.py` (optimizer logic)
- `grade_predictions_fixed.py` (grading logic)
- `dashboard_fixed.py` (metrics calculations)
- `enhanced_predictions.py` (prediction generation)

All database queries and logic already exist - just need to wrap in beautiful GUI!

---

**READY TO BUILD NEXT SESSION! 🚀**

This will be AMAZING! Your system will look like a professional betting platform! 💎
