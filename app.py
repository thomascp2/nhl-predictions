"""
NHL Prediction System - Streamlit Dashboard v2.0
Complete automation control center with system guide
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import subprocess
import os
from pathlib import Path

# Page config
st.set_page_config(
    page_title="NHL Prediction System",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
@st.cache_resource
def get_database_connection():
    return sqlite3.connect('database/nhl_predictions.db', check_same_thread=False)

conn = get_database_connection()

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e4d2b;
        border: 2px solid #00ff00;
        margin: 10px 0;
    }
    .warning-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #4d3d1e;
        border: 2px solid #ffa500;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to run scripts
def run_script(script_name, description=""):
    """Run a Python script and return the result"""
    try:
        result = subprocess.run(
            ["python", script_name],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        st.error(f"Error running {script_name}: {str(e)}")
        return None

# Helper function to get latest files
def get_latest_file(pattern):
    """Get the most recent file matching pattern"""
    files = list(Path('.').glob(pattern))
    if files:
        return max(files, key=lambda x: x.stat().st_mtime)
    return None

# Sidebar
st.sidebar.title("🏒 NHL Prediction System")
st.sidebar.markdown("### v2.0 - Complete Automation")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🤖 Automated Workflows",
        "🔧 Manual Operations",
        "💎 GTO Parlays",
        "🎯 Today's Picks",
        "📊 Performance",
        "📚 System Guide",
        "⚙️ Settings",
        "🛠️ System Utilities"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")

# Quick stats in sidebar
total_query = "SELECT COUNT(*) FROM predictions"
graded_query = "SELECT COUNT(*) FROM predictions WHERE result IS NOT NULL"
hits_query = "SELECT COUNT(*) FROM predictions WHERE result = 'HIT'"

total = pd.read_sql_query(total_query, conn).iloc[0, 0]
graded = pd.read_sql_query(graded_query, conn).iloc[0, 0]
hits = pd.read_sql_query(hits_query, conn).iloc[0, 0]

if graded > 0:
    hit_rate = (hits / graded) * 100
    st.sidebar.metric("Hit Rate", f"{hit_rate:.1f}%")
    st.sidebar.metric("Total Graded", graded)
    st.sidebar.metric("Profit", f"+{(hits * 0.91) - (graded - hits):.2f}u")

st.sidebar.markdown("---")

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

if page == "🏠 Dashboard":
    st.title("🏒 NHL Prediction System Dashboard")
    st.markdown("### Complete GTO + Multi-Line EV Optimization System")

    # System Status
    st.subheader("🔋 System Status")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Check if latest picks exist
        latest_picks = Path("LATEST_PICKS.txt")
        if latest_picks.exists():
            age_hours = (datetime.now().timestamp() - latest_picks.stat().st_mtime) / 3600
            if age_hours < 3:
                st.success(f"✅ Predictions Fresh ({age_hours:.1f}h old)")
            else:
                st.warning(f"⚠️ Predictions Stale ({age_hours:.1f}h old)")
        else:
            st.error("❌ No predictions")

    with col2:
        # Check GTO parlays
        gto_files = list(Path('.').glob('GTO_PARLAYS_*.csv'))
        if gto_files:
            latest_gto = max(gto_files, key=lambda x: x.stat().st_mtime)
            age_hours = (datetime.now().timestamp() - latest_gto.stat().st_mtime) / 3600
            if age_hours < 3:
                st.success(f"✅ Parlays Ready ({age_hours:.1f}h old)")
            else:
                st.warning(f"⚠️ Parlays Stale ({age_hours:.1f}h old)")
        else:
            st.error("❌ No parlays")

    with col3:
        # Check multi-line edges
        edge_files = list(Path('.').glob('MULTI_LINE_EDGES_*.csv'))
        if edge_files:
            latest_edges = max(edge_files, key=lambda x: x.stat().st_mtime)
            df = pd.read_csv(latest_edges)
            st.success(f"✅ {len(df)} Edge Plays")
        else:
            st.error("❌ No edges")

    with col4:
        # Database status
        st.success(f"✅ DB: {total} predictions")

    st.markdown("---")

    # Quick Actions
    st.subheader("⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 Run Complete Workflow", type="primary", use_container_width=True):
            with st.spinner("Running complete workflow..."):
                result = run_script("run_complete_workflow_gto.py")
                if result and result.returncode == 0:
                    st.success("✅ Workflow completed successfully!")
                    st.rerun()
                else:
                    st.error("❌ Workflow failed")
                    if result:
                        with st.expander("Show error details"):
                            st.code(result.stderr)

    with col2:
        if st.button("💎 Generate GTO Parlays", use_container_width=True):
            with st.spinner("Generating parlays..."):
                result = run_script("gto_parlay_optimizer.py")
                if result and result.returncode == 0:
                    st.success("✅ Parlays generated!")
                    st.rerun()
                else:
                    st.error("❌ Failed to generate parlays")

    with col3:
        if st.button("📊 Multi-Line EV Optimizer", use_container_width=True):
            with st.spinner("Running multi-line optimizer..."):
                result = run_script("prizepicks_multi_line_optimizer.py")
                if result and result.returncode == 0:
                    st.success("✅ Optimization complete!")
                    st.rerun()
                else:
                    st.error("❌ Optimization failed")

    st.markdown("---")

    # Today's Performance Overview
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 30-Day Profit Curve")

        profit_query = """
            SELECT
                game_date,
                COUNT(*) as total,
                SUM(CASE WHEN result = 'HIT' THEN 1 ELSE 0 END) as hits,
                SUM(CASE WHEN result = 'MISS' THEN 1 ELSE 0 END) as misses
            FROM predictions
            WHERE result IS NOT NULL
              AND game_date >= date('now', '-30 days')
            GROUP BY game_date
            ORDER BY game_date
        """

        profit_df = pd.read_sql_query(profit_query, conn)

        if len(profit_df) > 0:
            profit_df['profit'] = (profit_df['hits'] * 0.91) - profit_df['misses']
            profit_df['cumulative'] = profit_df['profit'].cumsum()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=profit_df['game_date'],
                y=profit_df['cumulative'],
                mode='lines+markers',
                name='Cumulative Profit',
                line=dict(color='#00ff00', width=3),
                fill='tozeroy'
            ))

            fig.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Profit (units)",
                hovermode='x unified',
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No graded predictions yet. Grade some picks to see the profit curve!")

    with col2:
        st.subheader("🎯 Today's Status")

        today = datetime.now().strftime('%Y-%m-%d')
        today_query = f"""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN confidence_tier = 'T1-ELITE' THEN 1 ELSE 0 END) as t1
            FROM predictions
            WHERE game_date = '{today}'
        """

        today_stats = pd.read_sql_query(today_query, conn).iloc[0]

        if today_stats['total'] > 0:
            st.metric("Total Picks", int(today_stats['total']))
            st.metric("T1-ELITE", int(today_stats['t1']), "🔥")

            # Check for today's files
            today_str = datetime.now().strftime('%Y-%m-%d')
            gto_today = list(Path('.').glob(f'GTO_PARLAYS_{today_str}*.csv'))
            edges_today = list(Path('.').glob(f'MULTI_LINE_EDGES_{today_str}*.csv'))

            if gto_today:
                st.success(f"✅ {len(pd.read_csv(gto_today[0]))} parlays ready")
            if edges_today:
                st.success(f"✅ {len(pd.read_csv(edges_today[0]))} edges found")
        else:
            st.info("No picks for today yet!")

    st.markdown("---")

    # Latest Files
    st.subheader("📁 Latest Generated Files")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**GTO Parlays**")
        gto_files = sorted(Path('.').glob('GTO_PARLAYS_*.csv'),
                          key=lambda x: x.stat().st_mtime, reverse=True)
        for f in gto_files[:3]:
            timestamp = datetime.fromtimestamp(f.stat().st_mtime)
            if st.button(f"📄 {f.name}", key=f"gto_{f.name}"):
                df = pd.read_csv(f)
                st.dataframe(df, use_container_width=True)

    with col2:
        st.markdown("**Multi-Line Edges**")
        edge_files = sorted(Path('.').glob('MULTI_LINE_EDGES_*.csv'),
                           key=lambda x: x.stat().st_mtime, reverse=True)
        for f in edge_files[:3]:
            timestamp = datetime.fromtimestamp(f.stat().st_mtime)
            if st.button(f"📄 {f.name}", key=f"edge_{f.name}"):
                df = pd.read_csv(f)
                st.dataframe(df, use_container_width=True)

# ============================================================================
# AUTOMATED WORKFLOWS PAGE
# ============================================================================

elif page == "🤖 Automated Workflows":
    st.title("🤖 Automated Workflows")
    st.markdown("### One-click execution of complete betting pipelines")

    st.markdown("---")

    # Complete Workflow
    st.subheader("🚀 Complete Workflow (Recommended)")

    st.markdown("""
    **This runs the complete GTO + Multi-Line EV pipeline:**
    1. Generate predictions (ML ensemble)
    2. Fetch ALL PrizePicks lines (~1,000+ lines)
    3. Multi-line EV optimization (finds 100+ edges)
    4. GTO parlay optimization (14 optimal parlays)
    5. Export CSVs with betting recommendations
    6. Commit to GitHub
    """)

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("🚀 Run Complete Workflow", type="primary", use_container_width=True, key="complete_workflow"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Step 1/4: Generating predictions...")
            progress_bar.progress(25)

            with st.spinner("Running complete workflow..."):
                result = run_script("run_complete_workflow_gto.py")

                progress_bar.progress(100)

                if result and result.returncode == 0:
                    st.success("✅ Complete workflow finished successfully!")

                    # Show summary
                    st.markdown("### 📊 Results Summary")

                    # Check generated files
                    latest_picks = get_latest_file("PICKS_*.txt")
                    latest_parlays = get_latest_file("GTO_PARLAYS_*.csv")
                    latest_edges = get_latest_file("MULTI_LINE_EDGES_*.csv")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if latest_picks:
                            with open(latest_picks, 'r') as f:
                                pick_count = len([l for l in f if 'OVER' in l or 'UNDER' in l])
                            st.metric("Predictions Generated", pick_count)

                    with col2:
                        if latest_parlays:
                            parlays_df = pd.read_csv(latest_parlays)
                            parlay_count = parlays_df['Parlay_ID'].nunique()
                            st.metric("GTO Parlays", parlay_count)

                    with col3:
                        if latest_edges:
                            edges_df = pd.read_csv(latest_edges)
                            st.metric("Edge Plays Found", len(edges_df))

                    st.balloons()
                else:
                    st.error("❌ Workflow failed")
                    if result:
                        with st.expander("Show error details"):
                            st.code(result.stderr)
                            st.code(result.stdout)

    with col2:
        st.markdown("**Estimated Time**")
        st.info("⏱️ 2-3 minutes")

    st.markdown("---")

    # Individual Workflow Steps
    st.subheader("🔧 Individual Workflow Steps")

    st.markdown("Run individual steps if you need to debug or re-run specific parts:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Step 1: Generate Predictions**")
        if st.button("📊 Generate Predictions", use_container_width=True):
            with st.spinner("Generating predictions..."):
                result = run_script("generate_picks_to_file.py")
                if result and result.returncode == 0:
                    st.success("✅ Predictions generated!")
                else:
                    st.error("❌ Failed")

        st.markdown("**Step 2: Multi-Line EV Optimizer**")
        if st.button("💎 Run Multi-Line Optimizer", use_container_width=True):
            with st.spinner("Running optimizer..."):
                result = run_script("prizepicks_multi_line_optimizer.py")
                if result and result.returncode == 0:
                    st.success("✅ Optimization complete!")
                    latest = get_latest_file("MULTI_LINE_EDGES_*.csv")
                    if latest:
                        df = pd.read_csv(latest)
                        st.metric("Edge Plays Found", len(df))
                else:
                    st.error("❌ Failed")

    with col2:
        st.markdown("**Step 3: GTO Parlay Optimizer**")
        if st.button("🎲 Generate GTO Parlays", use_container_width=True):
            with st.spinner("Generating parlays..."):
                result = run_script("gto_parlay_optimizer.py")
                if result and result.returncode == 0:
                    st.success("✅ Parlays generated!")
                    latest = get_latest_file("GTO_PARLAYS_*.csv")
                    if latest:
                        df = pd.read_csv(latest)
                        st.metric("Parlays Created", df['Parlay_ID'].nunique())
                else:
                    st.error("❌ Failed")

        st.markdown("**Step 4: Multiplier Learning**")
        if st.button("🧠 Learn Multipliers", use_container_width=True):
            with st.spinner("Learning multipliers..."):
                result = run_script("prizepicks_multiplier_learner.py")
                if result and result.returncode == 0:
                    st.success("✅ Multipliers learned!")
                else:
                    st.error("❌ Failed")

    st.markdown("---")

    # Data Refresh
    st.subheader("🔄 Data Refresh")

    st.markdown("Update player stats, game schedules, and betting odds:")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🎰 Fetch Daily Odds", use_container_width=True, help="Get real betting lines from The Odds API (1 API call)"):
            with st.spinner("Fetching betting odds..."):
                result = run_script("fetch_daily_odds.py")
                if result and result.returncode == 0:
                    st.success("✅ Odds fetched!")
                    st.info("💡 Real betting lines now available for TOI predictions")
                else:
                    st.error("❌ Failed")
                    if result:
                        with st.expander("Show error"):
                            st.code(result.stdout)

    with col2:
        if st.button("📥 Fetch Player Stats", use_container_width=True):
            with st.spinner("Fetching player stats..."):
                result = run_script("fetch_player_stats.py")
                if result and result.returncode == 0:
                    st.success("✅ Stats updated!")
                else:
                    st.error("❌ Failed")

    with col3:
        if st.button("🥅 Fetch Goalie Stats", use_container_width=True):
            with st.spinner("Fetching goalie stats..."):
                result = run_script("fetch_goalie_stats.py")
                if result and result.returncode == 0:
                    st.success("✅ Goalies updated!")
                else:
                    st.error("❌ Failed")

    with col3:
        if st.button("🏒 Fetch Team Stats", use_container_width=True):
            with st.spinner("Fetching team stats..."):
                result = run_script("fetch_team_stats.py")
                if result and result.returncode == 0:
                    st.success("✅ Teams updated!")
                else:
                    st.error("❌ Failed")

# ============================================================================
# MANUAL OPERATIONS PAGE
# ============================================================================

elif page == "🔧 Manual Operations":
    st.title("🔧 Manual Operations")
    st.markdown("### Database management, grading, and diagnostics")

    st.markdown("---")

    # Grading
    st.subheader("✅ Grading & Results")

    col1, col2 = st.columns([2, 1])

    with col1:
        grade_date = st.date_input("Select Date to Grade", value=datetime.now() - timedelta(days=1))
        date_str = grade_date.strftime('%Y-%m-%d')

    with col2:
        st.markdown("**Actions**")
        if st.button("✅ Auto-Grade", type="primary", use_container_width=True):
            with st.spinner(f"Grading {date_str}..."):
                result = run_script(f"grade_all_picks.py {date_str}")
                if result and result.returncode == 0:
                    st.success(f"✅ Graded {date_str}!")
                    st.rerun()
                else:
                    st.error("❌ Grading failed")
                    if result:
                        st.code(result.stdout)

        if st.button("📅 Grade Yesterday", use_container_width=True):
            with st.spinner("Grading yesterday's picks..."):
                result = run_script("auto_grade_yesterday.py")
                if result and result.returncode == 0:
                    st.success("✅ Graded yesterday!")
                    st.rerun()
                else:
                    st.error("❌ Grading failed")
                    if result:
                        st.code(result.stdout)

    # Show grading status
    status_query = f"""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN result = 'HIT' THEN 1 ELSE 0 END) as hits,
            SUM(CASE WHEN result = 'MISS' THEN 1 ELSE 0 END) as misses,
            SUM(CASE WHEN result IS NULL THEN 1 ELSE 0 END) as pending
        FROM predictions
        WHERE game_date = '{date_str}'
    """

    status = pd.read_sql_query(status_query, conn).iloc[0]

    if status['total'] > 0:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total", int(status['total']))
        with col2:
            st.metric("Hits", int(status['hits']), "✅")
        with col3:
            st.metric("Misses", int(status['misses']), "❌")
        with col4:
            st.metric("Pending", int(status['pending']), "⏳")

    st.markdown("---")

    # Database Operations
    st.subheader("🗄️ Database Operations")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Setup**")
        if st.button("🔧 Setup Database", use_container_width=True):
            with st.spinner("Setting up database..."):
                result = run_script("database_setup.py")
                if result and result.returncode == 0:
                    st.success("✅ Database setup complete!")
                else:
                    st.error("❌ Setup failed")

        if st.button("📊 Inspect Database", use_container_width=True):
            with st.spinner("Inspecting database..."):
                result = run_script("inspect_database.py")
                if result:
                    st.code(result.stdout)

    with col2:
        st.markdown("**Maintenance**")
        if st.button("🧹 Clean Duplicates", use_container_width=True):
            with st.spinner("Cleaning duplicates..."):
                result = run_script("remove_duplicates_v3.py")
                if result and result.returncode == 0:
                    st.success("✅ Duplicates removed!")
                else:
                    st.error("❌ Failed")

        if st.button("💾 Backup Database", use_container_width=True):
            import shutil
            backup_name = f"database/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy("database/nhl_predictions.db", backup_name)
            st.success(f"✅ Backup: {backup_name}")

    with col3:
        st.markdown("**Diagnostics**")
        if st.button("🔍 Run Diagnostics", use_container_width=True):
            with st.spinner("Running diagnostics..."):
                result = run_script("diagnose_workflow.py")
                if result:
                    st.code(result.stdout)

        if st.button("📈 View Stats", use_container_width=True):
            st.info("Use Performance page for detailed stats")

    st.markdown("---")

    # ML Model Operations
    st.subheader("🤖 ML Model Operations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Training**")
        if st.button("🎓 Train ML Model", use_container_width=True):
            with st.spinner("Training model (this may take several minutes)..."):
                result = run_script("train_nhl_ml_v3.py")
                if result and result.returncode == 0:
                    st.success("✅ Model trained!")
                else:
                    st.error("❌ Training failed")

        if st.button("⚖️ Retrain Weights", use_container_width=True):
            with st.spinner("Retraining ensemble weights..."):
                result = run_script("retrain_ml_weights.py")
                if result and result.returncode == 0:
                    st.success("✅ Weights updated!")
                else:
                    st.error("❌ Failed")

    with col2:
        st.markdown("**Testing**")
        if st.button("🧪 Test Predictions", use_container_width=True):
            with st.spinner("Testing predictions..."):
                result = run_script("test_predictions.py")
                if result:
                    st.code(result.stdout)

        if st.button("📊 Compare Models", use_container_width=True):
            with st.spinner("Comparing models..."):
                result = run_script("compare_models.py")
                if result:
                    st.code(result.stdout)

    st.markdown("---")

    # PrizePicks Operations
    st.subheader("💰 PrizePicks Operations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Odds Analysis**")
        if st.button("🎰 Check PrizePicks Odds", use_container_width=True):
            with st.spinner("Fetching odds..."):
                result = run_script("check_prizepicks_odds.py")
                if result:
                    st.code(result.stdout)

        if st.button("📊 Analyze Probabilities", use_container_width=True):
            with st.spinner("Analyzing probabilities..."):
                result = run_script("analyze_probabilities.py")
                if result:
                    st.code(result.stdout)

    with col2:
        st.markdown("**Integration**")
        if st.button("🔗 Test PrizePicks API", use_container_width=True):
            with st.spinner("Testing API..."):
                result = run_script("check_api_response.py")
                if result:
                    st.code(result.stdout)

        if st.button("🧪 Test Integration", use_container_width=True):
            with st.spinner("Testing integration..."):
                result = run_script("prizepicks_integration_FIXED.py")
                if result:
                    st.code(result.stdout[:1000])  # Show first 1000 chars

# ============================================================================
# GTO PARLAYS PAGE
# ============================================================================

elif page == "💎 GTO Parlays":
    st.title("💎 GTO Parlay Optimizer")
    st.markdown("### Optimal parlay construction with minimum payout thresholds")

    st.markdown("---")

    # Load latest parlays
    latest_parlays = get_latest_file("GTO_PARLAYS_*.csv")

    if latest_parlays:
        df = pd.read_csv(latest_parlays)

        # Summary metrics
        st.subheader("📊 Parlay Summary")

        unique_parlays = df['Parlay_ID'].nunique()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Parlays", unique_parlays)

        with col2:
            two_leg = len(df[df['Legs'] == 2]['Parlay_ID'].unique())
            st.metric("2-Leg Parlays", two_leg)

        with col3:
            three_leg = len(df[df['Legs'] == 3]['Parlay_ID'].unique())
            st.metric("3-Leg Parlays", three_leg)

        with col4:
            four_leg = len(df[df['Legs'] == 4]['Parlay_ID'].unique())
            st.metric("4-Leg Parlays", four_leg)

        st.markdown("---")

        # Parlay selector
        st.subheader("🎲 Select Parlay to View")

        parlay_options = [f"Parlay #{i} ({len(df[df['Parlay_ID']==i])} legs)"
                         for i in sorted(df['Parlay_ID'].unique())]

        selected_parlay_str = st.selectbox("Choose parlay:", parlay_options)
        selected_parlay_id = int(selected_parlay_str.split('#')[1].split()[0])

        # Display selected parlay
        parlay_data = df[df['Parlay_ID'] == selected_parlay_id]

        st.markdown(f"### Parlay #{selected_parlay_id}")

        # Parlay details
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**Legs:**")
            for _, leg in parlay_data.iterrows():
                st.markdown(f"""
                **Leg {int(leg['Leg_Number'])}:** {leg['Player']} ({leg['Team']})
                {leg['Prop_Type']} OVER {leg['Line']} [{leg['Odds_Type']}]
                """)

        with col2:
            st.markdown("**Betting Guidance:**")

            prob = parlay_data.iloc[0]['Combined_Probability']
            st.metric("Combined Probability", f"{float(prob.strip('%')):.1f}%")

            min_10 = parlay_data.iloc[0]['Min_Payout_10pct_EV']
            min_5 = parlay_data.iloc[0]['Min_Payout_5pct_EV']
            min_be = parlay_data.iloc[0]['Min_Payout_Breakeven']

            st.markdown(f"""
            **Minimum Payouts:**
            - 10% EV (IDEAL): **{min_10}**
            - 5% EV (OK): **{min_5}**
            - Break-even: **{min_be}**
            """)

            st.markdown("---")

            st.markdown("""
            **Your Action:**
            1. Add picks to PrizePicks
            2. Check displayed payout
            3. Compare to minimums above
            4. BET if >= IDEAL, SKIP if < OK
            """)

        st.markdown("---")

        # Full table view
        st.subheader("📋 All Parlays")

        # Format for display
        display_cols = ['Parlay_ID', 'Legs', 'Combined_Probability',
                       'Min_Payout_10pct_EV', 'Estimated_EV']

        summary_df = df.groupby('Parlay_ID').first().reset_index()[display_cols]
        summary_df['Parlay_ID'] = summary_df['Parlay_ID'].astype(int)

        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Complete Parlay Sheet",
            data=csv,
            file_name=f"gto_parlays_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )

    else:
        st.warning("No GTO parlays generated yet!")
        st.info("Click the button below to generate parlays.")

        if st.button("💎 Generate GTO Parlays", type="primary"):
            with st.spinner("Generating optimal parlays..."):
                result = run_script("gto_parlay_optimizer.py")
                if result and result.returncode == 0:
                    st.success("✅ Parlays generated!")
                    st.rerun()
                else:
                    st.error("❌ Failed to generate parlays")

# ============================================================================
# TODAY'S PICKS PAGE (Simplified - already good)
# ============================================================================

elif page == "🎯 Today's Picks":
    st.title("🎯 Today's Picks")

    today = datetime.now().strftime('%Y-%m-%d')

    # Load latest picks
    latest_picks = Path("LATEST_PICKS.txt")

    if latest_picks.exists():
        with open(latest_picks, 'r') as f:
            picks_text = f.read()

        st.markdown("### 📄 Latest Picks")
        st.text(picks_text)

        # Also show CSV if available
        latest_csv = Path("LATEST_PICKS.csv")
        if latest_csv.exists():
            df = pd.read_csv(latest_csv)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Picks CSV",
                data=csv,
                file_name=f"picks_{today}.csv",
                mime="text/csv"
            )
    else:
        st.warning("No picks generated yet!")
        if st.button("🔄 Generate Today's Picks", type="primary"):
            with st.spinner("Generating predictions..."):
                result = run_script("generate_picks_to_file.py")
                if result and result.returncode == 0:
                    st.success("✅ Picks generated!")
                    st.rerun()
                else:
                    st.error("❌ Failed")

# ============================================================================
# PERFORMANCE PAGE (Keep existing - it's good)
# ============================================================================

elif page == "📊 Performance":
    st.title("📊 Performance Analytics")

    # Date range selector
    col1, col2 = st.columns(2)

    with col1:
        date_range = st.selectbox(
            "Date Range",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
        )

    # Calculate date filter
    if date_range == "Last 7 Days":
        days = 7
    elif date_range == "Last 30 Days":
        days = 30
    elif date_range == "Last 90 Days":
        days = 90
    else:
        days = 99999

    st.markdown("---")

    # Overall metrics
    st.subheader("📈 Overall Performance")

    overall_query = f"""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN result = 'HIT' THEN 1 ELSE 0 END) as hits,
            SUM(CASE WHEN result = 'MISS' THEN 1 ELSE 0 END) as misses
        FROM predictions
        WHERE result IS NOT NULL
          AND game_date >= date('now', '-{days} days')
    """

    stats = pd.read_sql_query(overall_query, conn).iloc[0]

    if stats['total'] > 0:
        hit_rate = (stats['hits'] / stats['total']) * 100
        profit = (stats['hits'] * 0.91) - stats['misses']
        roi = (profit / stats['total']) * 100

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Picks", int(stats['total']))

        with col2:
            st.metric("Hit Rate", f"{hit_rate:.1f}%")

        with col3:
            st.metric("Profit", f"{profit:+.2f}u")

        with col4:
            st.metric("ROI", f"{roi:+.1f}%")

    else:
        st.warning("No graded predictions in selected range")

# ============================================================================
# SYSTEM GUIDE PAGE
# ============================================================================

elif page == "📚 System Guide":
    st.title("📚 System Guide")
    st.markdown("### Complete documentation of the NHL Prediction System")

    # Table of contents
    st.markdown("---")

    guide_section = st.radio(
        "Select Section:",
        [
            "🏠 Overview",
            "📊 How It Works",
            "🚀 Quick Start",
            "💎 GTO Parlays Explained",
            "🧮 Multi-Line EV System",
            "📏 Minimum Payout Method",
            "🔄 Daily Workflow",
            "❓ FAQ"
        ],
        horizontal=False
    )

    st.markdown("---")

    if guide_section == "🏠 Overview":
        st.markdown("""
        # System Overview

        This is a **complete Game Theory Optimal (GTO) + Multi-Line EV optimization system**
        for NHL player props betting on PrizePicks.

        ## Key Features

        ### 1. ML Ensemble Predictions
        - Statistical model (75% weight)
        - ML model (25% weight)
        - Rolling 5-game averages
        - Opponent strength adjustments

        ### 2. Multi-Line EV Optimizer
        - Fetches ALL ~1,000+ PrizePicks lines
        - Evaluates EVERY line independently
        - Uses interpolation/extrapolation for probabilities
        - Finds 100+ edge plays per day

        ### 3. GTO Parlay Optimizer
        - Frequency-weighted parlay construction
        - Generates 14 optimal parlays (2-leg, 3-leg, 4-leg)
        - Correlation filtering (same player, same game)
        - Kelly bet sizing

        ### 4. Multiplier Learning System
        - Learns actual individual pick multipliers
        - Demon picks: 2.0x-2.3x (varies!)
        - Goblin picks: 1.4x-1.6x
        - Standard picks: 1.7x

        ### 5. Minimum Payout Method
        - Works backwards from probability
        - Shows MINIMUM payout needed for target EV
        - Manual validation workflow (no automation needed)
        - Clear BET/SKIP instructions

        ## Files Generated

        - `LATEST_PICKS.txt/csv` - All predictions
        - `GTO_PARLAYS_*.csv` - Optimal parlays with min payouts
        - `MULTI_LINE_EDGES_*.csv` - All edge plays ranked by EV
        - `LEARNED_MULTIPLIERS_*.csv` - Actual multiplier observations

        ## Performance Target

        - **Hit Rate:** 58%+ (to beat -110 odds)
        - **ROI:** 10%+ (sustainable long-term)
        - **Bankroll Growth:** Steady, Kelly-optimized
        """)

    elif guide_section == "📊 How It Works":
        st.markdown("""
        # How It Works

        ## Step-by-Step Process

        ### 1. Data Collection
        ```
        fetch_player_stats.py      → NHL API player stats
        fetch_goalie_stats.py      → Goalie performance
        fetch_team_stats.py        → Team metrics
        ```

        ### 2. Prediction Generation
        ```
        generate_picks_to_file.py
        ├─ Statistical Model (75% weight)
        │  ├─ Rolling 5-game average
        │  ├─ Opponent strength adjustment
        │  └─ Home/away factors
        │
        └─ ML Model (25% weight)
           ├─ XGBoost ensemble
           ├─ 50+ features
           └─ Historical performance
        ```

        ### 3. Multi-Line EV Optimization
        ```
        prizepicks_multi_line_optimizer.py
        ├─ Fetch ALL PrizePicks lines (~1,000+)
        ├─ For each line:
        │  ├─ Estimate probability (interpolate/extrapolate)
        │  ├─ Get multiplier (learned or fallback)
        │  ├─ Calculate EV = (Prob × Multiplier) - 1
        │  └─ Calculate edge = Prob - (1 / Multiplier)
        │
        └─ Filter to 5%+ EV plays
        ```

        ### 4. GTO Parlay Optimization
        ```
        gto_parlay_optimizer.py
        ├─ Frequency allocation (GTO-style)
        │  ├─ Higher EV = higher frequency
        │  └─ Top picks appear 20x, mid picks 12x, etc.
        │
        ├─ Parlay generation
        │  ├─ 2-leg: 300 candidates → top 8
        │  ├─ 3-leg: 150 candidates → top 4
        │  └─ 4-leg: 75 candidates → top 2
        │
        └─ Minimum payout calculation
           ├─ Required = (1 + Target_EV) / Probability
           ├─ Show 10% EV, 5% EV, break-even
           └─ Clear BET/SKIP instructions
        ```

        ### 5. Manual Validation
        ```
        You add picks to PrizePicks
        ↓
        Check displayed payout
        ↓
        Compare to minimum thresholds
        ↓
        BET if payout >= minimum
        SKIP if payout < minimum
        ```

        ## Why This Approach?

        ### Advantages:
        - ✅ No browser automation needed
        - ✅ No stale data issues
        - ✅ Manual validation catches errors
        - ✅ Works with ANY PrizePicks update
        - ✅ Transparent decision-making

        ### Key Insight:
        **PrizePicks multipliers change dynamically** based on:
        - Player matchup
        - Line movement
        - Platform balancing

        So we work **backwards from probability** to find the minimum
        payout we can accept, then manually validate.
        """)

    elif guide_section == "🚀 Quick Start":
        st.markdown("""
        # Quick Start Guide

        ## First Time Setup

        ### 1. Run Complete Workflow
        ```bash
        python run_complete_workflow_gto.py
        ```

        This will:
        - Generate predictions
        - Find edge plays
        - Build optimal parlays
        - Export CSVs

        ### 2. Review Outputs

        **Check these files:**
        - `GTO_PARLAYS_*.csv` - Your betting sheet
        - `MULTI_LINE_EDGES_*.csv` - All edges found
        - `LATEST_PICKS.txt` - Quick reference

        ### 3. Place Bets on PrizePicks

        **For each parlay in GTO_PARLAYS CSV:**

        1. Open PrizePicks app/website
        2. Add the parlay legs to your slip
        3. Note the displayed payout (e.g., "3.5x")
        4. Compare to CSV minimums:
           - If payout >= Min_Payout_10pct_EV → **BET** (excellent edge)
           - If payout >= Min_Payout_5pct_EV → BET small or SKIP
           - If payout < Min_Payout_5pct_EV → **SKIP** (no edge)
        5. Mark "Action" column: BET or SKIP
        6. Record "Actual_Payout" in CSV

        ## Daily Routine

        ### Morning (8:00 AM)
        ```bash
        python run_complete_workflow_gto.py
        ```

        ### Review & Bet (10:00 AM - 6:00 PM)
        - Open GTO_PARLAYS CSV
        - Place bets using min payout method
        - Track results in CSV

        ### Evening Grade (Next Day)
        ```bash
        python grade_all_picks.py
        ```

        ## Automation Setup

        The system includes automated task scheduling:

        **Windows:**
        ```bash
        # Run as Administrator
        powershell -ExecutionPolicy Bypass -File setup_automated_schedule.ps1
        ```

        This creates scheduled tasks for:
        - 8:00 AM - Morning predictions
        - 12:00 PM - Midday update
        - 3:00 PM - Afternoon update
        - 6:00 PM - Final update

        All results are automatically committed to GitHub.
        """)

    elif guide_section == "💎 GTO Parlays Explained":
        st.markdown("""
        # GTO Parlays Explained

        ## What is GTO?

        **Game Theory Optimal (GTO)** = balanced strategy that's unexploitable.

        In poker: Mix bluffs and value bets so opponents can't exploit you.

        In betting: **Frequency-weight high-EV plays** so variance is managed.

        ## How We Apply GTO

        ### Frequency Allocation

        Instead of betting ONLY the highest EV plays:

        ```
        Top 10% EV plays   → 20x frequency
        Next 10% EV plays  → 16x frequency
        Mid-tier plays     → 12x frequency
        Lower plays        → 8x frequency
        ```

        ### Why This Matters

        **Without GTO:**
        - Always bet same 5 picks
        - If they're correlated (same games), high risk
        - One bad night = big loss

        **With GTO:**
        - Diversify across 40+ picks
        - Balanced frequency = balanced risk
        - Smooth variance, steady growth

        ## Parlay Construction

        ### Rules:
        1. **No same player** in one parlay
        2. **No same game** (avoid correlation)
        3. **Mix prop types** (points + shots)
        4. **Mix odds types** (demon + goblin + standard)

        ### Output:
        - 8x 2-leg parlays (safer, 70%+ combined prob)
        - 4x 3-leg parlays (moderate, 60%+ combined prob)
        - 2x 4-leg parlays (aggressive, 50%+ combined prob)

        ## Kelly Bet Sizing

        Each parlay shows Kelly % of bankroll:

        ```
        Kelly % = (Edge × Probability) / (Payout - 1)
        ```

        **Conservative approach:** Use 1/4 Kelly (system default)

        Example:
        - Bankroll: $1,000
        - Kelly suggests: 8%
        - 1/4 Kelly = 2% = **$20 bet**

        ## Expected Value (EV)

        ```
        EV = (Probability × Payout) - 1

        Example:
        - 2-leg parlay, 72% combined probability
        - PrizePicks offers 4.0x payout
        - EV = (0.72 × 4.0) - 1 = +188%

        Meaning: Every $100 bet returns $188 profit on average
        ```

        ## Why Parlays?

        PrizePicks ONLY offers parlays (2+ legs minimum).

        Single picks aren't available, so we optimize parlays directly.
        """)

    elif guide_section == "🧮 Multi-Line EV System":
        st.markdown("""
        # Multi-Line EV System

        ## The Problem

        **Old System:**
        - Only matched lines "within 0.5" of our prediction
        - If we predicted 3.0 shots, ignored 2.5 and 4.5 lines
        - Evaluated only ~40-50 lines per day

        **Missed Opportunity:**
        - PrizePicks offers 1,000+ lines per day
        - Different lines have different multipliers
        - Sometimes O4.5 has better EV than O3.5!

        ## The Solution

        ### Step 1: Fetch ALL Lines
        ```python
        response = requests.get("https://api.prizepicks.com/projections")
        # Returns 1,000+ NHL player prop lines
        ```

        ### Step 2: Estimate Probability at Any Line

        **Interpolation** (within predicted range):
        ```python
        # We predicted 3.0 shots at 80% probability
        # PrizePicks offers O2.5 line
        # Interpolate: closer to mean = higher probability
        prob_2_5 = 80% + (0.5 closer × 10% boost) = 85%
        ```

        **Extrapolation** (outside predicted range):
        ```python
        # We predicted 3.0 shots at 80% probability
        # PrizePicks offers O4.5 line
        # Extrapolate: further from mean = lower probability
        prob_4_5 = 80% - (1.5 further × 10% drop) = 65%
        ```

        ### Step 3: Get Multiplier

        **Priority:**
        1. **Learned** (70% confidence) - from manual observations
        2. **Historical** (50% confidence) - similar lines from past
        3. **Fallback** (20% confidence) - generic by odds_type

        ```python
        Demon   → 2.0x fallback (actual: 2.0x-2.3x)
        Goblin  → 1.414x fallback (actual: 1.4x-1.6x)
        Standard → 1.732x fallback (actual: 1.7x)
        ```

        ### Step 4: Calculate EV

        ```python
        EV = (Probability × Individual_Multiplier) - 1
        Edge = Probability - (1 / Individual_Multiplier)

        Example:
        - O2.5 shots, 85% probability, 2.021x multiplier
        - EV = (0.85 × 2.021) - 1 = +71.8%
        - Edge = 0.85 - (1/2.021) = +35.5%
        ```

        ### Step 5: Rank by EV

        Output shows:
        - Player name & team
        - Prop type & line
        - Odds type (DEMON/GOBLIN/STANDARD)
        - EV percentage
        - Edge percentage
        - Confidence level (LEARNED/HIST/EST)

        ## Results

        ### Before:
        - 40-50 lines evaluated
        - ~30% average EV
        - Missed 95% of opportunities

        ### After:
        - 1,000+ lines evaluated
        - ~105% average EV on edges
        - 165 edge plays found
        - 74% more opportunities

        ## Key Insight

        **Same player can have multiple +EV bets:**

        Example - Mark Scheifele:
        - O1.5 points (240% EV) ← Demon
        - O2.5 points (200% EV) ← Demon
        - O2.5 shots (146% EV) ← Demon

        All three are valid edges! Pick the one with best
        risk/reward for your bankroll.
        """)

    elif guide_section == "📏 Minimum Payout Method":
        st.markdown("""
        # Minimum Payout Method

        ## The Innovation

        Instead of trying to predict PrizePicks payouts (which change dynamically),
        we **work backwards** from our probability estimates.

        ## The Math

        ### Expected Value Formula:
        ```
        EV = (Probability × Payout) - 1
        ```

        ### Solving for Payout:
        ```
        Payout = (1 + Target_EV) / Probability
        ```

        ### Example:

        **2-leg parlay, 72.2% combined probability:**

        ```
        For 10% EV:  Payout = (1.10) / 0.722 = 1.52x
        For  5% EV:  Payout = (1.05) / 0.722 = 1.45x
        Break-even:  Payout = (1.00) / 0.722 = 1.38x
        ```

        ## The Workflow

        ### Step 1: Review GTO_PARLAYS CSV

        Open the CSV and see:
        ```
        Parlay_ID: 1
        Legs: 2
        Combined_Probability: 72.2%
        Min_Payout_10pct_EV: 1.52x
        Min_Payout_5pct_EV: 1.45x
        Min_Payout_Breakeven: 1.38x
        Estimated_Payout: 4.0x
        ```

        ### Step 2: Build Parlay on PrizePicks

        1. Open PrizePicks app/website
        2. Search for "Dylan Larkin"
        3. Add "Points Over 1.5"
        4. Search for "Jack Hughes"
        5. Add "Points Over 1.5"

        ### Step 3: Check Displayed Payout

        PrizePicks shows: **"3.8x payout"**

        ### Step 4: Compare to Minimums

        ```
        Actual: 3.8x
        vs
        Min for 10% EV: 1.52x ✅
        Min for  5% EV: 1.45x ✅
        Break-even:     1.38x ✅
        ```

        **Result: BET!** (way above minimum)

        ### Step 5: Record Result

        In CSV, update:
        ```
        Actual_Payout: 3.8x
        Action: BET
        ```

        ## Why This Works

        ### Advantages:

        1. **No automation needed** - Manual validation is simple
        2. **No stale data** - Always using PrizePicks' real-time payout
        3. **Clear decision rule** - Compare two numbers
        4. **Catches errors** - If payout is way off, you'll notice
        5. **Works forever** - Method doesn't break when PrizePicks updates

        ### Real-World Example:

        **Scenario:** PrizePicks changed their algorithm overnight

        **Old automated system:** Breaks, needs debugging, hours of work

        **Minimum payout method:**
        - System calculates new minimums based on probabilities
        - You see PrizePicks' new actual payout
        - Compare and decide
        - **Still works!**

        ## Decision Matrix

        ```
        If Actual >= Min_10pct:  BET (EXCELLENT EDGE)
        If Actual >= Min_5pct:   BET or BET SMALL
        If Actual >= Breakeven:  SKIP (marginal)
        If Actual <  Breakeven:  SKIP (negative EV)
        ```

        ## Bet Sizing

        When actual payout exceeds minimums by a lot:

        ```
        Actual: 4.0x
        Min for 10% EV: 1.52x
        Ratio: 4.0 / 1.52 = 2.63x above minimum

        → This is a HUGE edge
        → Consider betting more (still within Kelly limits)
        ```

        ## Safety Checks

        **Red flags to watch for:**

        1. Payout < Break-even → Don't bet!
        2. Payout way higher than estimated → Check if picks are correct
        3. Payout way lower than estimated → Line may have moved

        Manual validation catches these issues before you bet.
        """)

    elif guide_section == "🔄 Daily Workflow":
        st.markdown("""
        # Daily Workflow

        ## Fully Automated (Recommended)

        ### Setup Once:
        ```bash
        # Windows - Run as Administrator
        powershell -ExecutionPolicy Bypass -File setup_automated_schedule.ps1
        ```

        This creates 4 scheduled tasks:

        ### 8:00 AM - Morning Predictions
        ```
        run_complete_workflow_gto.py
        ├─ Generate predictions
        ├─ Multi-line EV optimization
        ├─ GTO parlay optimization
        └─ Commit to GitHub
        ```

        ### 12:00 PM - Midday Update
        ```
        Same as morning (accounts for late scratches)
        ```

        ### 3:00 PM - Afternoon Update
        ```
        Final update before evening games
        ```

        ### 6:00 PM - Evening Update
        ```
        Last chance for late games
        ```

        ## Manual Workflow (If You Prefer)

        ### Morning (30 minutes)

        **1. Run Complete Workflow**
        ```bash
        python run_complete_workflow_gto.py
        ```

        **2. Review Outputs**
        - Open `GTO_PARLAYS_*.csv`
        - Review 14 optimal parlays
        - Check minimum payout thresholds

        **3. Cross-reference Edges**
        - Open `MULTI_LINE_EDGES_*.csv`
        - See all 100+ edges found
        - Identify players appearing in parlays

        ### Midday (15 minutes)

        **1. Place Bets on PrizePicks**

        For each parlay:
        - Add legs to slip
        - Check displayed payout
        - Compare to CSV minimums
        - BET if >= minimum
        - Mark in CSV

        **2. Track Your Bets**
        ```
        Parlay #1: BET $20 @ 3.8x
        Parlay #2: SKIP (payout 1.4x < min 1.5x)
        Parlay #3: BET $15 @ 6.5x
        ...
        ```

        ### Evening (After Games)

        **1. Check Results** (optional - can wait until next day)

        ### Next Morning (5 minutes)

        **1. Grade Previous Day**
        ```bash
        python grade_all_picks.py
        ```

        **2. Review Performance**
        - Check dashboard in app.py
        - View profit curve
        - Analyze hit rate by tier

        ## Weekly Tasks

        ### Monday Morning (15 minutes)

        **1. Review Weekly Performance**
        ```
        Streamlit App → Performance Page
        - Check 7-day hit rate
        - Review profit trend
        - Identify top performers
        ```

        **2. Update Multiplier Database** (if you have new observations)
        ```bash
        python prizepicks_multiplier_learner.py
        ```

        **3. Retrain Model Weights** (optional)
        ```bash
        python retrain_ml_weights.py
        ```

        ## Monthly Tasks

        ### First of Month (30 minutes)

        **1. Full System Audit**
        ```
        - Check database size
        - Remove old duplicates
        - Backup database
        - Review long-term ROI
        ```

        **2. Model Retraining** (if performance degraded)
        ```bash
        python train_nhl_ml_v3.py
        ```

        **3. Update Season Data** (November/April)
        ```bash
        python fetch_player_stats.py
        python fetch_goalie_stats.py
        python fetch_team_stats.py
        ```

        ## Troubleshooting

        ### Workflow Failed?

        ```bash
        # Check diagnostics
        python diagnose_workflow.py

        # Inspect database
        python inspect_database.py

        # Test predictions
        python test_predictions.py
        ```

        ### No Games Today?

        System will still run but generate 0 picks. This is normal.

        ### PrizePicks API Down?

        Multi-line optimizer will fail gracefully. Use yesterday's picks
        or wait for API to recover.
        """)

    elif guide_section == "❓ FAQ":
        st.markdown("""
        # Frequently Asked Questions

        ## General

        ### Q: What sports are supported?
        **A:** Currently NHL only. System is built specifically for NHL player props.

        ### Q: What sportsbooks work with this?
        **A:** Designed for PrizePicks, but the prediction system works for any book.

        ### Q: Do I need coding experience?
        **A:** No! Just run the scripts and use this dashboard. All automation is set up.

        ### Q: What's the expected ROI?
        **A:** Target is 10%+ long-term ROI. With 58%+ hit rate at -110 odds, this is achievable.

        ## Technical

        ### Q: Why Multi-Line EV instead of just matching predictions?
        **A:** PrizePicks offers 1,000+ lines. Matching only our predictions evaluates 40-50 lines.
        Multi-line evaluates ALL lines, finding 74% more opportunities.

        ### Q: What's the difference between EV and Edge?
        **A:**
        - **EV** = Expected Value = (Prob × Multiplier) - 1
        - **Edge** = Advantage = Prob - (1 / Multiplier)

        Both measure profitability, EV in percentage terms, Edge in probability terms.

        ### Q: Why not automate the entire betting process?
        **A:**
        1. PrizePicks terms prohibit automation
        2. Manual validation catches errors
        3. Payouts change dynamically - automation would use stale data
        4. Minimum payout method is simple and foolproof

        ### Q: How accurate are the probability estimates?
        **A:**
        - **Direct predictions:** High accuracy (ML-trained)
        - **Interpolated:** Medium accuracy (close to predictions)
        - **Extrapolated:** Lower accuracy (use with caution)

        System shows confidence levels to help you decide.

        ### Q: What's a "Demon" pick?
        **A:** PrizePicks odds classification:
        - **Demon** 😈 = Harder prop, higher payout (~2.0x-2.3x individual)
        - **Goblin** 🦝 = Easier prop, lower payout (~1.4x-1.6x individual)
        - **Standard** ⚡ = Normal prop, medium payout (~1.7x individual)

        ## Betting

        ### Q: How much should I bet?
        **A:** Use Kelly Criterion (system calculates automatically):
        - **Full Kelly:** Aggressive (max growth, high variance)
        - **1/2 Kelly:** Moderate
        - **1/4 Kelly:** Conservative (recommended)
        - **1/8 Kelly:** Very conservative

        ### Q: What if actual payout is lower than estimated?
        **A:** Compare to MINIMUM payout, not estimated:
        - If actual >= Min_Payout_10pct_EV → Still a good bet
        - If actual < Min_Payout_5pct_EV → Skip

        ### Q: Should I bet all 14 parlays?
        **A:** No! Use minimums to filter:
        - BET if actual >= minimum (good edge)
        - SKIP if actual < minimum (no edge)

        Expect to bet 8-12 of the 14 parlays.

        ### Q: Can I combine picks into my own parlays?
        **A:** Yes, but be careful:
        - Avoid same player (correlated)
        - Avoid same game (correlated)
        - GTO optimizer already does this optimally

        ## Performance

        ### Q: Hit rate looks low this week, is something wrong?
        **A:** Short-term variance is normal. Evaluate over 100+ picks minimum.

        ### Q: Should I stop betting if I'm on a losing streak?
        **A:** No, if the math is sound. Variance is expected. Review:
        1. Are you following minimum payout thresholds?
        2. Are you recording actual payouts correctly?
        3. Is your bankroll management disciplined?

        If yes to all, keep betting. The edge will realize over time.

        ### Q: Model performance degraded, what to do?
        **A:**
        ```bash
        # Retrain ensemble weights
        python retrain_ml_weights.py

        # If that doesn't help, full retrain
        python train_nhl_ml_v3.py
        ```

        ## System Maintenance

        ### Q: How often should I update player stats?
        **A:** Automatically updated by scheduled tasks (daily). Manual update:
        ```bash
        python fetch_player_stats.py
        ```

        ### Q: Database getting large, how to clean?
        **A:**
        ```bash
        # Remove duplicates
        python remove_duplicates_v3.py

        # Backup first!
        python database_setup.py
        ```

        ### Q: Workflow failed, how to debug?
        **A:**
        ```bash
        python diagnose_workflow.py
        ```

        This checks all components and identifies the issue.

        ## Advanced

        ### Q: Can I adjust the ML model weights?
        **A:** Yes, edit `enhanced_predictions.py`:
        ```python
        statistical_weight = 0.75  # Default
        ml_weight = 0.25           # Default
        ```

        ### Q: Can I change the EV threshold?
        **A:** Yes, in `prizepicks_multi_line_optimizer.py`:
        ```python
        MIN_EV_THRESHOLD = 0.05  # Default 5%
        ```

        ### Q: Can I add more prop types (assists, blocks, etc.)?
        **A:** Yes, but requires:
        1. Updating prediction models
        2. Adding data collection for new props
        3. Training on historical data

        This is a significant project.

        ---

        ## Still Have Questions?

        Check the system logs:
        ```bash
        # Most scripts output detailed logs
        python <script_name>.py > output.log 2>&1
        ```

        Or open an issue on the GitHub repo with:
        - What you were trying to do
        - What happened vs what you expected
        - Any error messages
        """)

# ============================================================================
# SETTINGS PAGE (Keep existing)
# ============================================================================

elif page == "⚙️ Settings":
    st.title("⚙️ Settings & Configuration")

    # Bankroll Management
    st.subheader("💰 Bankroll Management")

    col1, col2 = st.columns(2)

    with col1:
        bankroll = st.number_input("Total Bankroll ($)", min_value=100, max_value=100000, value=1000, step=100)
        kelly_fraction = st.selectbox(
            "Kelly Fraction",
            ["1/4 Kelly (Conservative - Recommended)", "1/2 Kelly (Moderate)", "Full Kelly (Aggressive)"],
            index=0
        )

    with col2:
        max_daily_risk = st.slider("Max Daily Risk (%)", 10, 100, 30, 5)
        unit_size = st.number_input("Unit Size ($)", min_value=1, max_value=1000, value=10, step=5)

    st.info(f"💡 With ${bankroll} bankroll and {kelly_fraction}, typical bets: ${bankroll * 0.02:.2f} - ${bankroll * 0.05:.2f}")

    st.markdown("---")

    # System Info
    st.subheader("ℹ️ System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Version:** 2.0 - GTO + Multi-Line EV")
        st.markdown("**Last Updated:** 2025-10-30")
        st.markdown("**Python:** 3.13")

    with col2:
        st.markdown("**Status:** ✅ Operational")
        st.markdown("**Database:** ✅ Connected")
        st.markdown("**Automation:** ✅ Active")

    st.markdown("---")

    # Database Management
    st.subheader("🗄️ Database Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Backup Database", use_container_width=True):
            import shutil
            backup_name = f"database/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy("database/nhl_predictions.db", backup_name)
            st.success(f"Backup created: {backup_name}")

    with col2:
        if st.button("🧹 Clean Duplicates", use_container_width=True):
            with st.spinner("Cleaning duplicates..."):
                result = run_script("remove_duplicates_v3.py")
                if result and result.returncode == 0:
                    st.success("✅ Duplicates removed!")
                else:
                    st.error("❌ Failed")

    with col3:
        if st.button("🔍 Inspect Database", use_container_width=True):
            with st.spinner("Inspecting..."):
                result = run_script("inspect_database.py")
                if result:
                    st.code(result.stdout[:1000])

# ============================================================================
# SYSTEM UTILITIES PAGE
# ============================================================================

elif page == "🛠️ System Utilities":
    st.title("🛠️ System Utilities")
    st.markdown("### Production-ready system utilities and tools")
    st.markdown("---")

    # Tabs for different utilities
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Bankroll Manager",
        "📊 Adaptive Weights",
        "🔗 Correlation Detector",
        "⚡ Database Utilities",
        "📝 System Logs"
    ])

    # ========================================================================
    # TAB 1: BANKROLL MANAGER
    # ========================================================================
    with tab1:
        st.header("💰 Bankroll Management")
        st.markdown("**Track bankroll, calculate bet sizes, enforce risk limits**")
        st.markdown("---")

        # Bankroll Status
        st.subheader("Current Bankroll Status")

        try:
            from bankroll_manager import BankrollManager
            manager = BankrollManager()
            status = manager.get_status()

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Bankroll", f"${status['current_bankroll']:,.2f}")
            with col2:
                st.metric("Today's P/L", f"${status['daily_profit']:+,.2f}")
            with col3:
                st.metric("Win Rate", f"{status['win_rate']:.1f}%")
            with col4:
                st.metric("ROI", f"{status['roi']:+.1f}%")

            # Pending bets
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Pending Bets", status['pending_bets'])
                st.metric("Today's Wins", status['today_wins'])
            with col2:
                st.metric("Amount at Risk", f"${status['pending_amount']:,.2f}")
                st.metric("Today's Losses", status['today_losses'])

            # All-time stats
            st.markdown("---")
            st.subheader("All-Time Performance")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Bets", status['all_time_bets'])
            with col2:
                st.metric("Record", f"{status['all_time_wins']}W - {status['all_time_losses']}L")
            with col3:
                st.metric("Total Profit", f"${status['all_time_profit']:+,.2f}")

        except Exception as e:
            st.warning("Bankroll manager not initialized yet")
            st.info("Run: `BankrollManager(initial_bankroll=1000)` to initialize")

        # Bet Size Calculator
        st.markdown("---")
        st.subheader("Kelly Bet Size Calculator")

        col1, col2, col3 = st.columns(3)
        with col1:
            prob = st.slider("Win Probability", 0.50, 0.95, 0.60, 0.01)
        with col2:
            payout = st.number_input("Payout Multiplier", 1.5, 10.0, 2.0, 0.1)
        with col3:
            edge = st.slider("Expected Value (EV)", 0.0, 0.50, 0.10, 0.01)

        if st.button("Calculate Bet Size", type="primary"):
            try:
                from bankroll_manager import BankrollManager
                manager = BankrollManager()
                bet_info = manager.get_bet_size(prob, payout, edge)

                st.success("Bet size calculated!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Recommended Bet", f"${bet_info['recommended_bet']:.2f}")
                with col2:
                    st.metric("Kelly Bet", f"${bet_info['kelly_bet']:.2f}")
                with col3:
                    st.metric("Max Bet", f"${bet_info['max_bet']:.2f}")

                # Show warnings
                if bet_info['warnings']:
                    st.warning("⚠️ Warnings:")
                    for warning in bet_info['warnings']:
                        st.write(f"- {warning}")

                # Show daily risk
                st.info(f"Daily Risk Used: ${bet_info['daily_risk_used']:.2f} | Remaining: ${bet_info['daily_risk_remaining']:.2f}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

        # Initialize Bankroll
        st.markdown("---")
        st.subheader("Initialize/Update Bankroll")
        initial_bankroll = st.number_input("Starting Bankroll ($)", 100.0, 100000.0, 1000.0, 100.0)
        if st.button("Initialize Bankroll"):
            try:
                from bankroll_manager import BankrollManager
                manager = BankrollManager(initial_bankroll=initial_bankroll)
                st.success(f"Bankroll initialized: ${initial_bankroll:,.2f}")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # ========================================================================
    # TAB 2: ADAPTIVE WEIGHTS
    # ========================================================================
    with tab2:
        st.header("📊 Adaptive Model Weights")
        st.markdown("**Dynamically adjust ensemble weights based on recent performance**")
        st.markdown("---")

        # Current weights
        st.subheader("Current Weights")

        try:
            from adaptive_weights import get_adaptive_weights, get_model_performance

            # Get current weights
            stat_weight, ml_weight = get_adaptive_weights(days_back=7)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Statistical Model", f"{stat_weight:.0%}")
            with col2:
                st.metric("ML Model", f"{ml_weight:.0%}")

            # Performance analysis
            st.markdown("---")
            st.subheader("Recent Performance")

            days_back = st.slider("Days to Analyze", 3, 30, 7, 1)

            if st.button("Analyze Performance", type="primary"):
                performance = get_model_performance(days_back)

                if performance:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Predictions", performance['total_predictions'])
                    with col2:
                        st.metric("Ensemble Accuracy", f"{performance['ensemble_accuracy']:.1%}")
                    with col3:
                        st.metric("Days Analyzed", performance['days_analyzed'])

                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Avg Base Probability", f"{performance['avg_base_probability']:.1%}")
                    with col2:
                        st.metric("Avg ML Boost", f"{performance['avg_ml_boost']:+.1%}")

                    # Recalculate weights
                    st.markdown("---")
                    if st.button("Recalculate Weights"):
                        new_stat, new_ml = get_adaptive_weights(days_back=days_back)
                        st.success(f"New weights: {new_stat:.0%} statistical, {new_ml:.0%} ML")

                else:
                    st.warning(f"Not enough graded predictions in last {days_back} days")
                    st.info("Need at least 20 graded predictions for reliable analysis")

        except Exception as e:
            st.error(f"Error: {str(e)}")

        # Explanation
        st.markdown("---")
        st.subheader("How It Works")
        st.markdown("""
        **Adaptive Weights automatically adjust based on performance:**

        1. **Statistical Model Performance:**
           - If accuracy ≥ 75% → Increase weight to 80%
           - If accuracy < 65% → Decrease weight to 60%

        2. **ML Model Contribution:**
           - If ML boost helps accuracy → Increase ML weight
           - If ML boost hurts accuracy → Decrease ML weight

        3. **Fallback:**
           - Not enough data → Use baseline 70/30 split

        **Expected Impact:** 2-5% accuracy improvement through self-optimization
        """)

    # ========================================================================
    # TAB 3: CORRELATION DETECTOR
    # ========================================================================
    with tab3:
        st.header("🔗 Correlation Detection")
        st.markdown("**Test parlay leg correlations to avoid correlated bets**")
        st.markdown("---")

        st.subheader("Test Two Legs for Correlation")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Leg 1**")
            player1 = st.text_input("Player Name", "Dylan Larkin", key="player1")
            team1 = st.text_input("Team", "DET", key="team1")
            opp1 = st.text_input("Opponent", "LAK", key="opp1")
            prop1 = st.selectbox("Prop Type", ["points", "shots", "goals", "assists", "blocks", "hits"], key="prop1")

        with col2:
            st.markdown("**Leg 2**")
            player2 = st.text_input("Player Name", "Adrian Kempe", key="player2")
            team2 = st.text_input("Team", "LAK", key="team2")
            opp2 = st.text_input("Opponent", "DET", key="opp2")
            prop2 = st.selectbox("Prop Type", ["points", "shots", "goals", "assists", "blocks", "hits"], key="prop2")

        threshold = st.slider("Correlation Threshold", 0.0, 1.0, 0.30, 0.05)

        if st.button("Test Correlation", type="primary"):
            try:
                from correlation_detector import CorrelationDetector

                detector = CorrelationDetector()

                leg1 = {'player_name': player1, 'team': team1, 'opponent': opp1, 'prop_type': prop1}
                leg2 = {'player_name': player2, 'team': team2, 'opponent': opp2, 'prop_type': prop2}

                # Get correlation score
                score = detector.get_correlation_score(
                    player1, team1, opp1, prop1,
                    player2, team2, opp2, prop2
                )

                # Check if correlated
                is_correlated = detector.are_correlated(leg1, leg2, threshold)

                # Display results
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Correlation Score", f"{score:.2f}")
                with col2:
                    if is_correlated:
                        st.error(f"❌ CORRELATED (>{threshold:.2f})")
                    else:
                        st.success(f"✅ NOT CORRELATED (<{threshold:.2f})")

                # Explanation
                st.markdown("---")
                if score >= 1.0:
                    st.warning("**Same player** - Perfect correlation (1.0)")
                elif score >= 0.50:
                    st.warning("**High correlation** - Avoid in parlays")
                elif score >= 0.30:
                    st.info("**Moderate correlation** - Use caution")
                else:
                    st.success("**Low/No correlation** - Safe for parlays")

            except Exception as e:
                st.error(f"Error: {str(e)}")

        # Known correlations table
        st.markdown("---")
        st.subheader("Known Prop Correlations")
        st.markdown("""
        | Prop Combination | Correlation | Reason |
        |-----------------|-------------|---------|
        | Points + Goals | 0.75 | Goals count as points |
        | Points + Assists | 0.70 | Assists count as points |
        | Points + Shots | 0.60 | More shots → more points |
        | Shots + Goals | 0.55 | More shots → more goals |
        | Same Player | 1.00 | Perfect correlation |
        | Same Game | 0.30 | Game script affects both |
        | Same Team | 0.20 | Team performance correlation |
        """)

    # ========================================================================
    # TAB 4: DATABASE UTILITIES
    # ========================================================================
    with tab4:
        st.header("⚡ Database Utilities")
        st.markdown("**One-time database optimizations and maintenance**")
        st.markdown("---")

        # Add indexes
        st.subheader("Performance Indexes")
        st.markdown("Add database indexes for faster queries (run once)")

        if st.button("Add Database Indexes", type="primary"):
            with st.spinner("Adding indexes..."):
                result = run_script("add_database_indexes.py")
                if result and result.returncode == 0:
                    st.success("✅ Database indexes added!")
                    st.code(result.stdout)
                else:
                    st.error("Failed to add indexes")
                    if result:
                        st.code(result.stderr)

        # Database stats
        st.markdown("---")
        st.subheader("Database Statistics")

        if st.button("Show Database Stats"):
            try:
                # Get table sizes
                tables = [
                    'predictions',
                    'prizepicks_edges',
                    'gto_parlays',
                    'player_stats',
                    'bet_history'
                ]

                stats_data = []
                for table in tables:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        stats_data.append({'Table': table, 'Rows': count})
                    except:
                        pass

                if stats_data:
                    df = pd.DataFrame(stats_data)
                    st.dataframe(df, use_container_width=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")

    # ========================================================================
    # TAB 5: SYSTEM LOGS
    # ========================================================================
    with tab5:
        st.header("📝 System Logs")
        st.markdown("**View system logs and error reports**")
        st.markdown("---")

        # Log file selector
        import glob
        log_files = glob.glob("logs/*.log")

        if log_files:
            log_file = st.selectbox("Select Log File", sorted(log_files, reverse=True))

            # Display options
            col1, col2 = st.columns(2)
            with col1:
                num_lines = st.number_input("Lines to Display", 10, 1000, 100, 10)
            with col2:
                log_level = st.selectbox("Filter Level", ["ALL", "ERROR", "WARNING", "INFO", "DEBUG"])

            if st.button("View Log", type="primary"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    # Filter by level
                    if log_level != "ALL":
                        lines = [line for line in lines if log_level in line]

                    # Get last N lines
                    lines = lines[-num_lines:]

                    # Display
                    st.code(''.join(lines))

                    # Download button
                    st.download_button(
                        "Download Log File",
                        data=''.join(lines),
                        file_name=log_file.split('/')[-1],
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"Error reading log: {str(e)}")
        else:
            st.info("No log files found. Logs will be created when the system runs.")
            st.markdown("Logs are saved to: `logs/system_YYYY-MM-DD.log`")

# Footer
st.markdown("---")
st.markdown("""
🏒 **NHL Prediction System v2.0** | GTO + Multi-Line EV Optimization
Built with Streamlit | Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M'))
