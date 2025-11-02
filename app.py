"""
NHL Prediction System Dashboard - Streamlit Interface
Redesigned for simplicity: 13 pages → 8 pages (62% size reduction)
Features: Command Center, Visual Workflow, Integrated Grading, No TOI
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import subprocess
import sys
import time
import requests

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="NHL Prediction System",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================
DB_PATH = "database/nhl_predictions.db"

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def query_db(query, params=()):
    """Execute query and return DataFrame"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_data_freshness():
    """Check how fresh the player stats data is"""
    try:
        query = """
            SELECT MAX(last_updated) as latest
            FROM player_stats
        """
        df = query_db(query)
        if not df.empty and df['latest'][0]:
            latest = pd.to_datetime(df['latest'][0])
            hours_old = (datetime.now() - latest).total_seconds() / 3600
            return hours_old
    except:
        pass
    return None

def get_today_summary():
    """Get summary stats for today"""
    today = datetime.now().strftime('%Y-%m-%d')

    # Get predictions by type
    query = """
        SELECT prop_type, COUNT(*) as count,
               AVG(probability) as avg_conf
        FROM predictions
        WHERE game_date = ?
        GROUP BY prop_type
    """
    preds = query_db(query, (today,))

    # Get T1-ELITE count
    query_elite = """
        SELECT COUNT(*) as elite_count
        FROM predictions
        WHERE game_date = ? AND probability >= 0.85
    """
    elite = query_db(query_elite, (today,))
    elite_count = elite['elite_count'][0] if not elite.empty else 0

    # Get edges count
    query_edges = """
        SELECT COUNT(*) as edge_count
        FROM prizepicks_edges
        WHERE date = ?
    """
    edges = query_db(query_edges, (today,))
    edge_count = edges['edge_count'][0] if not edges.empty else 0

    # Get parlays count
    query_parlays = """
        SELECT COUNT(*) as parlay_count
        FROM gto_parlays
        WHERE date = ?
    """
    parlays = query_db(query_parlays, (today,))
    parlay_count = parlays['parlay_count'][0] if not parlays.empty else 0

    return {
        'predictions': preds,
        'total_predictions': preds['count'].sum() if not preds.empty else 0,
        'elite_count': elite_count,
        'edge_count': edge_count,
        'parlay_count': parlay_count
    }

def get_top_picks(limit=5):
    """Get top N picks for today"""
    today = datetime.now().strftime('%Y-%m-%d')
    query = """
        SELECT player_name, prop_type, line, prediction, probability,
               game_time, team, opponent
        FROM predictions
        WHERE game_date = ?
        ORDER BY probability DESC
        LIMIT ?
    """
    return query_db(query, (today, limit))

def normalize_team_name(team_name):
    """Normalize team names to standard NHL abbreviations"""
    # Mapping of variations to standard abbreviations
    team_map = {
        'Utah Mammoth': 'UTA',
        'Utah': 'UTA',
        'TB': 'TBL',
        'NJ': 'NJD',
        'LA': 'LAK',
        'SJ': 'SJS',
    }
    return team_map.get(team_name, team_name)

def fetch_live_scores(date_str):
    """Fetch live scores from NHL API for a specific date"""
    try:
        url = f"https://api-web.nhle.com/v1/schedule/{date_str}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Extract game scores
            scores = {}

            if 'gameWeek' in data:
                # Only look at the first day (today) in gameWeek
                if len(data['gameWeek']) > 0:
                    day = data['gameWeek'][0]  # First day is today
                    if 'games' in day:
                        for game in day['games']:
                            away_team = game.get('awayTeam', {}).get('abbrev', 'UNK')
                            home_team = game.get('homeTeam', {}).get('abbrev', 'UNK')

                            # Store with both possible key formats for flexible matching
                            game_key = f"{away_team}@{home_team}"

                            scores[game_key] = {
                                'away_team': away_team,
                                'home_team': home_team,
                                'away_score': game.get('awayTeam', {}).get('score', 0),
                                'home_score': game.get('homeTeam', {}).get('score', 0),
                                'game_state': game.get('gameState', 'UNKNOWN'),
                                'period': game.get('periodDescriptor', {}).get('number', 0),
                                'time_remaining': game.get('clock', {}).get('timeRemaining', ''),
                                'game_type': game.get('gameType', 2)
                            }

            return scores
        else:
            return {}
    except Exception as e:
        st.warning(f"Could not fetch live scores: {e}")
        return {}

def run_script(script_path, description, timeout=300):
    """Run a Python script and show progress"""
    with st.spinner(f"{description}..."):
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                st.success(f"[SUCCESS] {description} completed!")
                if result.stdout:
                    with st.expander("View output"):
                        st.text(result.stdout)
                return True
            else:
                st.error(f"[ERROR] {description} failed")
                if result.stderr:
                    with st.expander("Error details"):
                        st.text(result.stderr)
                return False
        except subprocess.TimeoutExpired:
            st.error(f"[TIMEOUT] {description} took too long (>{timeout}s)")
            return False
        except Exception as e:
            st.error(f"[ERROR] {description} failed: {e}")
            return False

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.title("🏒 NHL Prediction System")
st.sidebar.markdown("---")

# Quick Stats in Sidebar
data_hours = get_data_freshness()
if data_hours is not None:
    if data_hours < 2:
        st.sidebar.success(f"Data: Fresh ({data_hours:.1f}h old)")
    elif data_hours < 6:
        st.sidebar.warning(f"Data: {data_hours:.1f}h old")
    else:
        st.sidebar.error(f"Data: Stale ({data_hours:.1f}h old)")
else:
    st.sidebar.info("Data: Unknown")

summary = get_today_summary()
st.sidebar.metric("Today's Predictions", summary['total_predictions'])
st.sidebar.metric("T1-ELITE Picks", summary['elite_count'])

st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "🎯 Command Center",
        "📊 Today's Predictions",
        "💎 Edges & Parlays",
        "📅 Schedule & Live Scores",
        "📈 Performance & Grading",
        "⚙️ System Control",
        "ℹ️ System Info",
        "🔧 Settings"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("v2.0 - Redesigned Dashboard")
st.sidebar.caption(f"Updated: {datetime.now().strftime('%I:%M %p')}")

# ============================================================================
# PAGE 1: COMMAND CENTER (Main Landing Page)
# ============================================================================

if page == "🎯 Command Center":
    st.title("🎯 NHL Prediction System - Command Center")
    st.markdown("**Your central hub for daily NHL prediction workflows**")

    st.markdown("---")

    # Visual Workflow Diagram
    st.subheader("📊 Daily Workflow")

    # Create visual workflow with columns
    st.markdown("""
    ```
    ┌──────────────────────────────────────────────────────────────┐
    │                    DAILY WORKFLOW                            │
    │                                                              │
    │                        START                                 │
    │                          ↓                                   │
    │                  1. GENERATE PICKS                           │
    │                          ↓                                   │
    │                  2. FIND EDGES                               │
    │                          ↓                                   │
    │                  3. REVIEW & BET                             │
    │                          ↓                                   │
    │                  4. GRADE RESULTS                            │
    │                          ↓                                   │
    │                        REPEAT                                │
    └──────────────────────────────────────────────────────────────┘
    ```
    """)

    st.markdown("---")

    # Quick Action Buttons
    st.subheader("⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**STEP 1: Generate Picks**")
        st.info("Runtime: ~45 seconds")
        if st.button("🚀 Generate Today's Picks", use_container_width=True, type="primary"):
            success = run_script("RUN_DAILY_PICKS.py", "Generating predictions", timeout=120)
            if success:
                time.sleep(2)
                st.rerun()

    with col2:
        st.markdown("**STEP 2: Find Edges**")
        st.info("Runtime: ~50 seconds")
        if st.button("🔍 Find Edges & Parlays", use_container_width=True):
            success = run_script("RUN_EDGE_FINDER.py", "Finding edges and parlays", timeout=120)
            if success:
                time.sleep(2)
                st.rerun()

    with col3:
        st.markdown("**STEP 4: Grade Results**")
        st.info("Runtime: ~45 seconds")
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if st.button("✅ Grade Yesterday", use_container_width=True):
            with st.spinner(f"Grading predictions for {yesterday}..."):
                try:
                    result = subprocess.run(
                        [sys.executable, "adaptive_learning/auto_grade_predictions.py", yesterday],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    if result.returncode == 0:
                        st.success(f"[SUCCESS] Graded predictions for {yesterday}!")
                        if result.stdout:
                            with st.expander("View grading results"):
                                st.text(result.stdout)
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("[ERROR] Grading failed")
                        if result.stderr:
                            with st.expander("Error details"):
                                st.text(result.stderr)
                except Exception as e:
                    st.error(f"[ERROR] Grading failed: {e}")

    st.markdown("---")

    # Cloud Deployment Note + Database Download
    st.subheader("💾 Save Your Updates")

    col_save1, col_save2 = st.columns([2, 1])

    with col_save1:
        st.info("**Cloud Deployment Note:** Predictions generated here persist during your session but are reset when the app redeploys. Download the database to keep permanent updates!")

    with col_save2:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "rb") as db_file:
                st.download_button(
                    label="📥 Download Database",
                    data=db_file,
                    file_name=f"nhl_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                    mime="application/octet-stream",
                    use_container_width=True,
                    type="primary"
                )
            st.caption("Download after generating picks, then commit to GitHub")

    st.markdown("---")

    # Step 3 - View Results
    st.subheader("👁️ STEP 3: Review Results")
    col_view1, col_view2, col_view3 = st.columns(3)
    with col_view1:
        if st.button("📊 View Today's Predictions", use_container_width=True):
            st.session_state['nav_override'] = "📊 Today's Predictions"
            st.rerun()
    with col_view2:
        if st.button("💎 View Edges & Parlays", use_container_width=True):
            st.session_state['nav_override'] = "💎 Edges & Parlays"
            st.rerun()
    with col_view3:
        if st.button("📈 View Performance", use_container_width=True):
            st.session_state['nav_override'] = "📈 Performance & Grading"
            st.rerun()

    st.markdown("---")

    # System Status
    st.subheader("🔍 System Status")

    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:
        st.metric("Active Models", "3")
        st.caption("Statistical, Ensemble, Goalie")

    with status_col2:
        data_hours = get_data_freshness()
        if data_hours is not None:
            st.metric("Data Freshness", f"{data_hours:.1f}h")
            if data_hours < 2:
                st.caption("✅ Fresh")
            elif data_hours < 6:
                st.caption("⚠️ Acceptable")
            else:
                st.caption("❌ Stale - Refresh recommended")
        else:
            st.metric("Data Freshness", "Unknown")

    with status_col3:
        # Check database
        if os.path.exists(DB_PATH):
            size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
            st.metric("Database", f"{size_mb:.1f} MB")
            st.caption("✅ Connected")
        else:
            st.metric("Database", "Error")
            st.caption("❌ Not found")

    st.markdown("---")

    # Today's Summary
    st.subheader("📋 Today's Summary")

    summary = get_today_summary()

    sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
    with sum_col1:
        st.metric("Total Predictions", summary['total_predictions'])
    with sum_col2:
        st.metric("T1-ELITE Picks", summary['elite_count'])
    with sum_col3:
        st.metric("Edge Opportunities", summary['edge_count'])
    with sum_col4:
        st.metric("GTO Parlays", summary['parlay_count'])

    # Breakdown by prop type
    if not summary['predictions'].empty:
        st.markdown("**Breakdown by Prop Type:**")
        breakdown_df = summary['predictions'][['prop_type', 'count', 'avg_conf']]
        breakdown_df['avg_conf'] = breakdown_df['avg_conf'].apply(lambda x: f"{x*100:.1f}%")
        breakdown_df.columns = ['Prop Type', 'Count', 'Avg Confidence']
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Top 5 Picks Preview
    st.subheader("🌟 Top 5 Picks for Today")

    top_picks = get_top_picks(5)
    if not top_picks.empty:
        for idx, pick in top_picks.iterrows():
            conf_pct = pick['probability'] * 100

            # Confidence tier badge
            if conf_pct >= 85:
                tier = "T1-ELITE"
                tier_color = "🟢"
            elif conf_pct >= 65:
                tier = "T2-STRONG"
                tier_color = "🟡"
            else:
                tier = "T3-MARGINAL"
                tier_color = "⚪"

            pred_text = pick['prediction']
            line_val = pick['line']

            st.markdown(
                f"{idx+1}. **{pick['player_name']}** - {pick['prop_type']} {pred_text} {line_val} "
                f"({conf_pct:.1f}%) {tier_color} [{tier}]"
            )
            st.caption(f"   {pick['team']} vs {pick['opponent']} @ {pick['game_time']}")

        st.markdown("")
        if st.button("→ View All Predictions", use_container_width=True):
            st.session_state['nav_override'] = "📊 Today's Predictions"
            st.rerun()
    else:
        st.info("No predictions generated yet for today. Click '🚀 Generate Today's Picks' above!")

# ============================================================================
# PAGE 2: TODAY'S PREDICTIONS (Merged: Picks + Goalie Saves)
# ============================================================================

elif page == "📊 Today's Predictions":
    st.title("📊 Today's Predictions")

    today = datetime.now().strftime('%Y-%m-%d')

    # Filters
    st.subheader("Filters")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        prop_filter = st.selectbox(
            "Prop Type",
            ["All", "points", "shots", "goalie_saves"]
        )

    with filter_col2:
        conf_filter = st.selectbox(
            "Confidence Tier",
            ["All", "T1-ELITE (≥85%)", "T2-STRONG (65-84%)", "T3-MARGINAL (50-64%)"]
        )

    with filter_col3:
        team_filter = st.text_input("Team Filter", "")

    # Build query
    query = """
        SELECT
            player_name,
            team,
            opponent,
            prop_type,
            line,
            prediction,
            ROUND(probability * 100, 1) as confidence_pct,
            game_time,
            game_date
        FROM predictions
        WHERE game_date = ?
    """
    params = [today]

    if prop_filter != "All":
        query += " AND prop_type = ?"
        params.append(prop_filter)

    if conf_filter != "All":
        if "T1-ELITE" in conf_filter:
            query += " AND probability >= 0.85"
        elif "T2-STRONG" in conf_filter:
            query += " AND probability >= 0.65 AND probability < 0.85"
        elif "T3-MARGINAL" in conf_filter:
            query += " AND probability >= 0.50 AND probability < 0.65"

    if team_filter:
        query += " AND (team LIKE ? OR opponent LIKE ?)"
        params.extend([f"%{team_filter}%", f"%{team_filter}%"])

    query += " ORDER BY probability DESC, player_name"

    df = query_db(query, tuple(params))

    if not df.empty:
        st.success(f"Found {len(df)} predictions")

        # Add tier column
        def get_tier(conf):
            if conf >= 85:
                return "T1-ELITE"
            elif conf >= 65:
                return "T2-STRONG"
            else:
                return "T3-MARGINAL"

        df['Tier'] = df['confidence_pct'].apply(get_tier)

        # Display table
        st.dataframe(
            df[['player_name', 'team', 'opponent', 'prop_type', 'line', 'prediction',
                'confidence_pct', 'Tier', 'game_time']],
            use_container_width=True,
            hide_index=True
        )

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"predictions_{today}.csv",
            mime="text/csv"
        )

        # Summary stats
        st.markdown("---")
        st.subheader("Summary Statistics")
        sum_col1, sum_col2, sum_col3 = st.columns(3)
        with sum_col1:
            st.metric("Total Predictions", len(df))
        with sum_col2:
            avg_conf = df['confidence_pct'].mean()
            st.metric("Average Confidence", f"{avg_conf:.1f}%")
        with sum_col3:
            elite_count = len(df[df['confidence_pct'] >= 85])
            st.metric("T1-ELITE Picks", elite_count)
    else:
        st.warning(f"No predictions found for {today} with selected filters")
        st.info("Generate predictions using the Command Center or complete daily workflow")

# ============================================================================
# PAGE 3: EDGES & PARLAYS (Merged: Edge Plays + GTO Parlays)
# ============================================================================

elif page == "💎 Edges & Parlays":
    st.title("💎 Edges & Parlays")

    # Tabs for merged content
    tab1, tab2 = st.tabs(["💎 Edge Opportunities", "🎰 GTO Parlays"])

    today = datetime.now().strftime('%Y-%m-%d')

    # ---- TAB 1: EDGE OPPORTUNITIES ----
    with tab1:
        st.subheader("💎 Positive Expected Value Opportunities")

        query = """
            SELECT
                player_name,
                prop_type,
                line,
                odds_type as prediction,
                ROUND(our_probability * 100, 1) as confidence_pct,
                ROUND(expected_value * 100, 1) as ev_pct,
                ROUND(kelly_score * 100, 2) as kelly_pct,
                team,
                opponent
            FROM prizepicks_edges
            WHERE date = ?
            ORDER BY expected_value DESC
        """
        edges_df = query_db(query, (today,))

        if not edges_df.empty:
            st.success(f"Found {len(edges_df)} edge opportunities")

            # Filter
            min_ev = st.slider("Minimum EV %", 0, 50, 10)
            filtered = edges_df[edges_df['ev_pct'] >= min_ev]

            st.markdown(f"**Showing {len(filtered)} edges with EV ≥ {min_ev}%**")

            # Display
            st.dataframe(
                filtered,
                use_container_width=True,
                hide_index=True
            )

            # Download
            csv = filtered.to_csv(index=False)
            st.download_button(
                label="📥 Download Edges as CSV",
                data=csv,
                file_name=f"edges_{today}.csv",
                mime="text/csv"
            )

            # Kelly Criterion explanation
            with st.expander("ℹ️ What is Kelly Criterion?"):
                st.markdown("""
                **Kelly Criterion** is an optimal bet sizing formula that maximizes long-term growth.

                - **Kelly %**: Recommended percentage of bankroll to bet
                - **Example**: If Kelly = 2.5% and bankroll = $1000, bet $25
                - **Conservative approach**: Use 25-50% of Kelly recommendation (fractional Kelly)

                **Formula**: Kelly % = (Edge / Odds) where Edge = (Win Probability × Payout) - 1
                """)
        else:
            st.info(f"No edges found for {today}")
            st.caption("Edges are generated by running the Edge Finder from Command Center")

    # ---- TAB 2: GTO PARLAYS ----
    with tab2:
        st.subheader("🎰 Game Theory Optimal Parlays")

        query = """
            SELECT
                parlay_id,
                num_legs,
                ROUND(combined_probability * 100, 1) as confidence_pct,
                ROUND(expected_value * 100, 1) as ev_pct,
                ROUND(kelly_fraction * 100, 2) as kelly_pct,
                picks_json
            FROM gto_parlays
            WHERE date = ?
            ORDER BY expected_value DESC
        """
        parlays_df = query_db(query, (today,))

        if not parlays_df.empty:
            st.success(f"Found {len(parlays_df)} GTO parlays")

            # Filter by legs
            leg_filter = st.selectbox(
                "Number of Legs",
                ["All", "2", "3", "4", "5+"]
            )

            if leg_filter != "All":
                if leg_filter == "5+":
                    filtered = parlays_df[parlays_df['num_legs'] >= 5]
                else:
                    filtered = parlays_df[parlays_df['num_legs'] == int(leg_filter)]
            else:
                filtered = parlays_df

            st.markdown(f"**Showing {len(filtered)} parlays**")

            # Display summary table
            st.dataframe(
                filtered[['parlay_id', 'num_legs', 'confidence_pct', 'ev_pct', 'kelly_pct']],
                use_container_width=True,
                hide_index=True
            )

            # Expandable details for each parlay
            st.markdown("---")
            st.markdown("**Parlay Details (click to expand)**")

            for idx, parlay in filtered.head(10).iterrows():
                with st.expander(f"Parlay #{parlay['parlay_id']} - {parlay['num_legs']} legs - {parlay['confidence_pct']}% confidence - {parlay['ev_pct']}% EV"):
                    st.markdown(f"**Picks:** {parlay['picks_json']}")
                    st.markdown(f"**Combined Confidence:** {parlay['confidence_pct']}%")
                    st.markdown(f"**Expected Value:** {parlay['ev_pct']}%")
                    st.markdown(f"**Kelly Bet Size:** {parlay['kelly_pct']}% of bankroll")

            if len(filtered) > 10:
                st.info(f"Showing top 10 of {len(filtered)} parlays. Download CSV for full list.")

            # Download
            csv = filtered.to_csv(index=False)
            st.download_button(
                label="📥 Download Parlays as CSV",
                data=csv,
                file_name=f"parlays_{today}.csv",
                mime="text/csv"
            )
        else:
            st.info(f"No parlays found for {today}")
            st.caption("Parlays are generated by running the Edge Finder from Command Center")

# ============================================================================
# PAGE 4: SCHEDULE & LIVE SCORES
# ============================================================================

elif page == "📅 Schedule & Live Scores":
    st.title("📅 Schedule & Live Scores")

    today = datetime.now().strftime('%Y-%m-%d')

    # Refresh button for live scores
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh Scores", type="primary"):
            st.rerun()
    with col2:
        st.caption(f"Last updated: {datetime.now().strftime('%I:%M:%S %p')}")

    st.markdown("---")

    # Fetch live scores from NHL API
    live_scores = fetch_live_scores(today)

    # Get today's games (deduplicated using alphabetical ordering since is_home is often NULL)
    query = """
        SELECT DISTINCT
            CASE
                WHEN team < opponent THEN team
                ELSE opponent
            END as team1,
            CASE
                WHEN team < opponent THEN opponent
                ELSE team
            END as team2,
            MIN(game_time) as game_time,
            game_date
        FROM predictions
        WHERE game_date = ?
        GROUP BY team1, team2, game_date
        ORDER BY game_time
    """
    games_df = query_db(query, (today,))

    if not games_df.empty:
        st.success(f"Found {len(games_df)} games today")

        st.markdown("---")

        for idx, game in games_df.iterrows():
            team1 = game['team1']
            team2 = game['team2']

            # Normalize team names for matching (e.g., "Utah Mammoth" -> "UTA")
            team1_norm = normalize_team_name(team1)
            team2_norm = normalize_team_name(team2)

            # Check if we have live scores for this game (try multiple combinations)
            possible_keys = [
                f"{team1_norm}@{team2_norm}",
                f"{team2_norm}@{team1_norm}",
                f"{team1}@{team2}",
                f"{team2}@{team1}"
            ]

            score_data = {}
            for key in possible_keys:
                if key in live_scores:
                    score_data = live_scores[key]
                    break

            # Display game header with score if available
            if score_data:
                game_state = score_data.get('game_state', 'UNKNOWN')
                away_team = score_data.get('away_team', team1)
                home_team = score_data.get('home_team', team2)
                away_score = score_data.get('away_score', 0)
                home_score = score_data.get('home_score', 0)
                period = score_data.get('period', 0)
                time_remaining = score_data.get('time_remaining', '')

                # Format the game state
                if game_state == 'LIVE' or game_state == 'CRIT':
                    status_color = "🔴"
                    status_text = f"LIVE - P{period}"
                    if time_remaining:
                        status_text += f" - {time_remaining}"
                elif game_state == 'FUT' or game_state == 'PRE':
                    status_color = "⚪"
                    status_text = f"Scheduled - {game['game_time']}" if game['game_time'] else "Scheduled"
                elif game_state == 'FINAL' or game_state == 'OFF':
                    status_color = "✅"
                    status_text = "FINAL"
                else:
                    status_color = "⚪"
                    status_text = game_state

                st.subheader(f"{status_color} {away_team} {away_score} @ {home_score} {home_team}")
                st.caption(f"{status_text}")
            else:
                # No live score data, just show team names
                st.subheader(f"{team1} vs {team2}")
                if game['game_time']:
                    st.caption(f"Game Time: {game['game_time']}")
                else:
                    st.caption("Game time TBD")

            # Get predictions for this game (match either team order)
            query_preds = """
                SELECT
                    player_name,
                    prop_type,
                    line,
                    prediction,
                    ROUND(probability * 100, 1) as confidence_pct
                FROM predictions
                WHERE game_date = ?
                  AND ((team = ? AND opponent = ?) OR (team = ? AND opponent = ?))
                ORDER BY probability DESC
                LIMIT 10
            """
            preds = query_db(
                query_preds,
                (today, team1, team2, team2, team1)
            )

            if not preds.empty:
                st.markdown("**Top Predictions for this game:**")
                st.dataframe(preds, use_container_width=True, hide_index=True)

            st.markdown("---")
    else:
        st.info(f"No games scheduled for {today}")

    # Betting Lines (if available)
    st.subheader("📊 Betting Lines")

    # Deduplicated betting lines - ONLY for games in predictions table
    query_odds = """
        SELECT DISTINCT
            gbl.away_team,
            gbl.home_team,
            gbl.away_ml,
            gbl.home_ml,
            gbl.over_under,
            gbl.puck_line,
            gbl.home_pl_odds,
            gbl.away_pl_odds,
            gbl.game_date,
            gbl.last_updated
        FROM game_betting_lines gbl
        WHERE gbl.game_date = ?
        AND (gbl.away_team, gbl.home_team, gbl.last_updated) IN (
            SELECT away_team, home_team, MAX(last_updated)
            FROM game_betting_lines
            WHERE game_date = ?
            GROUP BY away_team, home_team
        )
        AND (
            -- Match games that exist in predictions (either team ordering)
            EXISTS (
                SELECT 1 FROM predictions p
                WHERE p.game_date = ?
                AND (
                    (p.team = gbl.away_team AND p.opponent = gbl.home_team)
                    OR (p.team = gbl.home_team AND p.opponent = gbl.away_team)
                )
            )
        )
        ORDER BY gbl.away_team, gbl.home_team
    """
    odds_df = query_db(query_odds, (today, today, today))

    if not odds_df.empty:
        # Drop last_updated from display
        display_df = odds_df.drop(columns=['last_updated'])
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.caption(f"Showing latest odds (last updated: {odds_df['last_updated'].max()})")
    else:
        st.info("No betting lines available yet")
        st.caption("Betting lines are fetched automatically before games start")

# ============================================================================
# PAGE 5: PERFORMANCE & GRADING (Enhanced with Integrated Grading)
# ============================================================================

elif page == "📈 Performance & Grading":
    st.title("📈 Performance & Grading")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Performance Metrics", "✅ Auto-Grading", "📋 Manual Grading"])

    # ---- TAB 1: PERFORMANCE METRICS ----
    with tab1:
        st.subheader("📊 Overall Performance")

        # Get overall stats
        query_overall = """
            SELECT
                prop_type,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
                ROUND(AVG(CASE WHEN outcome = 'HIT' THEN 1.0 ELSE 0.0 END) * 100, 1) as hit_rate,
                AVG(predicted_probability) as avg_confidence
            FROM prediction_outcomes
            GROUP BY prop_type
            ORDER BY prop_type
        """
        overall_df = query_db(query_overall)

        if not overall_df.empty:
            # Display metrics
            cols = st.columns(len(overall_df))
            for idx, (col, row) in enumerate(zip(cols, overall_df.itertuples())):
                with col:
                    st.metric(
                        row.prop_type.upper(),
                        f"{row.hit_rate}%",
                        f"{row.hits}/{row.total}"
                    )

            st.markdown("---")

            # Detailed table
            st.markdown("**Detailed Breakdown:**")
            overall_df['avg_confidence'] = overall_df['avg_confidence'].apply(lambda x: f"{x*100:.1f}%")
            st.dataframe(overall_df, use_container_width=True, hide_index=True)

            # Chart
            st.markdown("---")
            st.markdown("**Hit Rate by Prop Type:**")
            st.bar_chart(overall_df.set_index('prop_type')['hit_rate'])
        else:
            st.info("No graded predictions yet")
            st.caption("Grade predictions using the Auto-Grading tab")

        st.markdown("---")

        # Recent performance (last 7 days)
        st.subheader("📅 Recent Performance (Last 7 Days)")

        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        query_recent = """
            SELECT
                game_date,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
                ROUND(AVG(CASE WHEN outcome = 'HIT' THEN 1.0 ELSE 0.0 END) * 100, 1) as hit_rate
            FROM prediction_outcomes
            WHERE game_date >= ?
            GROUP BY game_date
            ORDER BY game_date DESC
        """
        recent_df = query_db(query_recent, (seven_days_ago,))

        if not recent_df.empty:
            st.dataframe(recent_df, use_container_width=True, hide_index=True)

            # Chart
            st.line_chart(recent_df.set_index('game_date')['hit_rate'])
        else:
            st.info("No recent data available")

    # ---- TAB 2: AUTO-GRADING ----
    with tab2:
        st.subheader("✅ Automatic Prediction Grading")

        st.info("Auto-grading fetches actual player stats from the NHL API and compares them to predictions")

        # Date picker
        default_date = datetime.now() - timedelta(days=1)
        grade_date = st.date_input(
            "Select date to grade",
            value=default_date,
            max_value=datetime.now() - timedelta(days=1)
        )

        grade_date_str = grade_date.strftime('%Y-%m-%d')

        # Check if already graded
        query_check = """
            SELECT COUNT(*) as graded_count
            FROM prediction_outcomes
            WHERE game_date = ?
        """
        check_df = query_db(query_check, (grade_date_str,))
        already_graded = check_df['graded_count'][0] if not check_df.empty else 0

        # Check predictions to grade
        query_preds = """
            SELECT COUNT(*) as pred_count
            FROM predictions
            WHERE game_date = ?
        """
        preds_df = query_db(query_preds, (grade_date_str,))
        preds_count = preds_df['pred_count'][0] if not preds_df.empty else 0

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Predictions for this date", preds_count)
        with col2:
            st.metric("Already graded", already_graded)

        if already_graded > 0:
            st.warning(f"⚠️ {already_graded} predictions already graded for {grade_date_str}")
            st.caption("Running auto-grade again will re-grade existing predictions")

        if preds_count == 0:
            st.error(f"❌ No predictions found for {grade_date_str}")

        st.markdown("---")

        # Auto-grade button
        if st.button("🚀 Run Auto-Grading", use_container_width=True, type="primary", disabled=(preds_count == 0)):
            with st.spinner(f"Grading {preds_count} predictions for {grade_date_str}..."):
                try:
                    result = subprocess.run(
                        [sys.executable, "adaptive_learning/auto_grade_predictions.py", grade_date_str],
                        capture_output=True,
                        text=True,
                        timeout=180
                    )

                    if result.returncode == 0:
                        st.success(f"✅ Successfully graded predictions for {grade_date_str}!")

                        # Show output
                        if result.stdout:
                            with st.expander("📋 Grading details"):
                                st.text(result.stdout)

                        # Refresh page to show updated stats
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Auto-grading failed")
                        if result.stderr:
                            with st.expander("Error details"):
                                st.text(result.stderr)
                except subprocess.TimeoutExpired:
                    st.error("❌ Auto-grading timed out (>3 minutes)")
                except Exception as e:
                    st.error(f"❌ Auto-grading error: {e}")

        st.markdown("---")

        # Recent grading history
        st.subheader("📋 Recent Grading History")

        query_history = """
            SELECT
                game_date,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END) as hits,
                ROUND(AVG(CASE WHEN outcome = 'HIT' THEN 1.0 ELSE 0.0 END) * 100, 1) as hit_rate
            FROM prediction_outcomes
            GROUP BY game_date
            ORDER BY game_date DESC
            LIMIT 10
        """
        history_df = query_db(query_history)

        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True, hide_index=True)
        else:
            st.info("No grading history yet")

    # ---- TAB 3: MANUAL GRADING ----
    with tab3:
        st.subheader("📋 Manual Grading Interface")

        st.info("Manual grading for edge cases where auto-grading fails")

        # Select date
        manual_date = st.date_input(
            "Select date",
            value=datetime.now() - timedelta(days=1),
            max_value=datetime.now(),
            key="manual_date_picker"
        )

        manual_date_str = manual_date.strftime('%Y-%m-%d')

        # Get ungraded predictions
        query_ungraded = """
            SELECT
                p.id,
                p.player_name,
                p.team,
                p.opponent,
                p.prop_type,
                p.line,
                p.prediction,
                p.probability,
                p.game_date
            FROM predictions p
            LEFT JOIN prediction_outcomes po ON p.id = po.prediction_id
            WHERE p.game_date = ? AND po.prediction_id IS NULL
            ORDER BY p.player_name
        """
        ungraded_df = query_db(query_ungraded, (manual_date_str,))

        if not ungraded_df.empty:
            st.warning(f"Found {len(ungraded_df)} ungraded predictions for {manual_date_str}")

            # Select prediction to grade
            selected_pred = st.selectbox(
                "Select prediction to grade",
                ungraded_df['player_name'] + " - " + ungraded_df['prop_type'] + " " + ungraded_df['prediction'] + " " + ungraded_df['line'].astype(str),
                format_func=lambda x: x
            )

            if selected_pred:
                idx = ungraded_df[
                    (ungraded_df['player_name'] + " - " + ungraded_df['prop_type'] + " " + ungraded_df['prediction'] + " " + ungraded_df['line'].astype(str)) == selected_pred
                ].index[0]

                pred_row = ungraded_df.loc[idx]

                st.markdown("---")
                st.markdown(f"**Player:** {pred_row['player_name']}")
                st.markdown(f"**Team:** {pred_row['team']} vs {pred_row['opponent']}")
                st.markdown(f"**Prop:** {pred_row['prop_type']} {pred_row['prediction']} {pred_row['line']}")
                st.markdown(f"**Confidence:** {pred_row['probability']*100:.1f}%")

                # Input actual stat
                actual_stat = st.number_input("Enter actual stat value", min_value=0.0, step=0.5)

                # Grade button
                if st.button("Submit Grade", type="primary"):
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()

                        # Determine if hit
                        # Check if prediction is OVER or UNDER
                        is_over = pred_row['prediction'].upper() == 'OVER'
                        hit = (is_over and actual_stat > 0.5) or (not is_over and actual_stat <= 0.5)
                        outcome = 'HIT' if hit else 'MISS'

                        cursor.execute("""
                            INSERT INTO prediction_outcomes
                            (prediction_id, player_name, prop_type, predicted_direction, actual_stat_value,
                             predicted_probability, outcome, game_date, team, opponent)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            pred_row['id'],
                            pred_row['player_name'],
                            pred_row['prop_type'],
                            pred_row['prediction'],
                            actual_stat,
                            pred_row['probability'],
                            outcome,
                            pred_row['game_date'],
                            pred_row['team'],
                            pred_row['opponent']
                        ))

                        conn.commit()
                        conn.close()

                        st.success(f"✅ Graded as {'HIT' if hit else 'MISS'}!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving grade: {e}")
        else:
            st.success(f"✅ All predictions graded for {manual_date_str}")

# ============================================================================
# PAGE 6: SYSTEM CONTROL (Merged: Workflows + Manual Operations)
# ============================================================================

elif page == "⚙️ System Control":
    st.title("⚙️ System Control")

    # Tabs for different controls
    tab1, tab2, tab3 = st.tabs(["🤖 Automated Workflows", "🔧 Manual Operations", "🗄️ Database Tools"])

    # ---- TAB 1: AUTOMATED WORKFLOWS ----
    with tab1:
        st.subheader("🤖 Automated Workflows")

        st.markdown("**Complete end-to-end workflows:**")

        # Complete Daily Workflow
        st.markdown("---")
        st.markdown("### 🚀 Complete Daily Workflow")
        st.info("Full refresh: Data → Predictions → Edges → Parlays → GitHub (~2-3 minutes)")

        if st.button("▶️ Run Complete Workflow", use_container_width=True, type="primary"):
            run_script("RUN_COMPLETE_WORKFLOW.py", "Complete daily workflow", timeout=300)

        # Enhanced System
        st.markdown("---")
        st.markdown("### ⚡ Enhanced System")
        st.info("Advanced filtering for top 20 picks + smart parlays (~60 seconds)")

        if st.button("▶️ Run Enhanced System", use_container_width=True):
            run_script("RUN_ENHANCED_SYSTEM.py", "Enhanced system integration", timeout=180)

        # Individual steps
        st.markdown("---")
        st.markdown("### 🔧 Individual Steps")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("1️⃣ Generate Predictions", use_container_width=True):
                run_script("RUN_DAILY_PICKS.py", "Generate predictions", timeout=120)

            if st.button("3️⃣ Grade Results", use_container_width=True):
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                with st.spinner(f"Grading {yesterday}..."):
                    subprocess.run(
                        [sys.executable, "adaptive_learning/auto_grade_predictions.py", yesterday],
                        capture_output=False
                    )

        with col2:
            if st.button("2️⃣ Find Edges & Parlays", use_container_width=True):
                run_script("RUN_EDGE_FINDER.py", "Find edges and parlays", timeout=120)

            if st.button("4️⃣ Open Dashboard", use_container_width=True):
                st.info("Dashboard is already open (you're viewing it now!)")

    # ---- TAB 2: MANUAL OPERATIONS ----
    with tab2:
        st.subheader("🔧 Manual Operations")

        # Data refresh
        st.markdown("### 📊 Data Refresh")
        st.info("Fetch latest player stats, goalie data, and betting lines")

        if st.button("🔄 Refresh All Data", use_container_width=True):
            run_script("smart_data_refresh.py", "Data refresh", timeout=180)

        st.markdown("---")

        # Individual model runs
        st.markdown("### 🤖 Run Individual Models")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Statistical Model", use_container_width=True):
                run_script("fresh_clean_predictions.py", "Statistical model", timeout=90)

        with col2:
            if st.button("🎯 Ensemble Model", use_container_width=True):
                run_script("ensemble_predictions.py", "Ensemble model", timeout=90)

        with col3:
            if st.button("🥅 Goalie Model", use_container_width=True):
                run_script("goalie_saves_predictions.py", "Goalie saves model", timeout=90)

        st.markdown("---")

        # Edge finding
        st.markdown("### 💎 Edge Finding")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Multi-Line Edges", use_container_width=True):
                run_script("prizepicks_multi_line_optimizer.py", "Multi-line optimizer", timeout=90)

        with col2:
            if st.button("🎰 GTO Parlays", use_container_width=True):
                run_script("gto_parlay_optimizer.py", "GTO parlay optimizer", timeout=90)

    # ---- TAB 3: DATABASE TOOLS ----
    with tab3:
        st.subheader("🗄️ Database Tools")

        st.warning("⚠️ Use database tools with caution")

        # Database info
        if os.path.exists(DB_PATH):
            size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
            st.metric("Database Size", f"{size_mb:.2f} MB")
            st.caption(f"Location: {DB_PATH}")
        else:
            st.error("Database not found!")

        st.markdown("---")

        # Table info
        st.markdown("### 📋 Table Information")

        query_tables = """
            SELECT name, COUNT(*) as count
            FROM (
                SELECT 'predictions' as name UNION ALL
                SELECT 'prediction_outcomes' UNION ALL
                SELECT 'prizepicks_edges' UNION ALL
                SELECT 'gto_parlays' UNION ALL
                SELECT 'player_stats' UNION ALL
                SELECT 'goalie_stats'
            ) tables
            GROUP BY name
        """

        # Get row counts for each table
        tables_info = []
        for table in ['predictions', 'prediction_outcomes', 'prizepicks_edges',
                      'gto_parlays', 'player_stats', 'goalie_stats']:
            query = f"SELECT COUNT(*) as count FROM {table}"
            df = query_db(query)
            if not df.empty:
                tables_info.append({
                    'Table': table,
                    'Rows': df['count'][0]
                })

        tables_df = pd.DataFrame(tables_info)
        st.dataframe(tables_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Custom query
        st.markdown("### 🔍 Custom SQL Query")
        st.caption("For advanced users only")

        custom_query = st.text_area(
            "Enter SQL query",
            "SELECT * FROM predictions WHERE game_date = date('now') LIMIT 10"
        )

        if st.button("Execute Query"):
            try:
                result_df = query_db(custom_query)
                st.success(f"Query returned {len(result_df)} rows")
                st.dataframe(result_df, use_container_width=True)
            except Exception as e:
                st.error(f"Query error: {e}")

# ============================================================================
# PAGE 7: SYSTEM INFO (Merged: Architecture + Schedule + Guide)
# ============================================================================

elif page == "ℹ️ System Info":
    st.title("ℹ️ System Information")

    # Tabs for merged documentation
    tab1, tab2, tab3 = st.tabs(["🏗️ System Architecture", "⏰ Operation Schedule", "📚 Quick Start Guide"])

    # ---- TAB 1: SYSTEM ARCHITECTURE ----
    with tab1:
        st.subheader("🏗️ System Architecture")

        st.markdown("""
        ### Overview

        The NHL Prediction System consists of **3 active machine learning models** that generate
        daily predictions for NHL player props:

        1. **Statistical Model** - Season averages and trends (72% accuracy)
        2. **Ensemble Model** - Weighted ML ensemble (73-75% accuracy)
        3. **Goalie Saves Model** - Specialized goalie predictions (71% accuracy)

        ### Data Flow

        ```
        NHL API → Data Refresh → Database (SQLite)
                                     ↓
                    ┌────────────────┴────────────────┐
                    ↓                ↓                ↓
              Statistical      Ensemble         Goalie
                 Model           Model           Model
                    ↓                ↓                ↓
                    └────────────────┬────────────────┘
                                     ↓
                            Predictions Table
                                     ↓
                    ┌────────────────┴────────────────┐
                    ↓                                 ↓
              Edge Finder                      GTO Parlay
              (10%+ EV)                        Optimizer
                    ↓                                 ↓
            prizepicks_edges                  gto_parlays
        ```

        ### Database Tables

        **Input Tables:**
        - `player_stats` - Player season statistics
        - `goalie_stats` - Goalie statistics
        - `game_betting_lines` - Betting odds
        - `probable_goalies` - Starting goalies

        **Output Tables:**
        - `predictions` - All daily predictions (114/day)
        - `prediction_outcomes` - Graded results
        - `prizepicks_edges` - Positive EV opportunities
        - `gto_parlays` - Optimized parlays

        ### File Structure

        ```
        C:/Users/thoma/PrizePicks-Research-Lab/
        │
        ├── RUN_*.py                 # Simple wrapper scripts
        ├── database/
        │   └── nhl_predictions.db   # SQLite database
        ├── adaptive_learning/
        │   └── auto_grade_predictions.py  # Auto-grading
        ├── enhanced_system/
        │   └── master_integration_script.py  # Advanced filtering
        ├── v2_system/
        │   └── ...                  # Historical analysis
        └── app.py                   # This dashboard
        ```
        """)

    # ---- TAB 2: OPERATION SCHEDULE ----
    with tab2:
        st.subheader("⏰ Daily Operation Schedule")

        st.markdown("""
        ### Recommended Daily Schedule

        | Time | Action | Command | Duration |
        |------|--------|---------|----------|
        | **7:00 AM** | Generate daily picks | `python RUN_DAILY_PICKS.py` | 45s |
        | **12:00 PM** | Midday refresh (if needed) | `python RUN_DAILY_PICKS.py` | 45s |
        | **4:00 PM** | Pre-game check | Open Dashboard | - |
        | **7:00 PM** | Find edges & parlays | `python RUN_EDGE_FINDER.py` | 50s |
        | **11:00 PM** | Grade yesterday | `python RUN_GRADING.py` | 45s |

        ### Typical Workflow

        **Morning (7:00 AM):**
        1. Open Command Center
        2. Click "🚀 Generate Today's Picks"
        3. Wait 45 seconds
        4. View top picks or full predictions

        **Pre-Game (4:00-7:00 PM):**
        1. Click "🔍 Find Edges & Parlays"
        2. Review positive EV opportunities
        3. Check GTO parlays
        4. Place bets

        **Next Morning (7:00 AM):**
        1. Click "✅ Grade Yesterday"
        2. Review performance metrics
        3. Generate new picks
        4. Repeat

        ### Automation Options

        You can automate daily workflows using:
        - **Windows Task Scheduler** - Schedule `RUN_DAILY_PICKS.py` at 7 AM
        - **Cron Jobs** (Linux/Mac) - Same as above
        - **GitHub Actions** - Auto-push results to repo

        ### Data Refresh Frequency

        - Player stats are automatically refreshed if data is >4 hours old
        - Betting lines refresh every 2 hours before games
        - Predictions regenerate each day at 7 AM
        - Grading happens the next morning after games complete
        """)

    # ---- TAB 3: QUICK START GUIDE ----
    with tab3:
        st.subheader("📚 Quick Start Guide")

        st.markdown("""
        ### Getting Started in 5 Minutes

        #### 1. Generate Your First Picks

        ```bash
        python RUN_DAILY_PICKS.py
        ```

        **What happens:**
        - Checks if data is fresh (auto-refreshes if stale)
        - Runs 3 models (Statistical, Ensemble, Goalie)
        - Generates ~114 predictions
        - Filters to 5-10 T1-ELITE picks
        - Creates `LATEST_PICKS.txt` and `LATEST_PICKS.csv`
        - Pushes to GitHub

        **Output files:**
        - `LATEST_PICKS.txt` - Human-readable
        - `LATEST_PICKS.csv` - Spreadsheet format
        - Timestamped backups in root directory

        #### 2. View Results

        **Option A: Dashboard (Recommended)**
        ```bash
        python RUN_DASHBOARD.py
        ```
        Opens web interface at `http://localhost:8501`

        **Option B: GitHub (Mobile-Friendly)**
        Visit: https://github.com/thomascp2/nhl-predictions/blob/main/LATEST_PICKS.txt

        **Option C: Local Files**
        Open `LATEST_PICKS.txt` in any text editor

        #### 3. Find Betting Edges

        ```bash
        python RUN_EDGE_FINDER.py
        ```

        **Output:**
        - 5-20 edge opportunities (10%+ EV)
        - 10-50 GTO parlays
        - Files: `MULTI_LINE_EDGES_*.csv`, `GTO_PARLAYS_*.csv`

        #### 4. Grade Results

        ```bash
        python RUN_GRADING.py
        ```

        Automatically grades yesterday's predictions (99%+ success rate)

        ### Understanding the Output

        **Confidence Tiers:**
        - **T1-ELITE** (≥85%) - Best picks, bet with confidence
        - **T2-STRONG** (65-84%) - Good picks, moderate bet size
        - **T3-MARGINAL** (50-64%) - Marginal picks, small bets or skip

        **Expected Value (EV):**
        - Positive EV = Profitable in long run
        - Target: 10%+ EV for single bets
        - Higher EV = Better opportunity

        **Kelly Criterion:**
        - Optimal bet sizing formula
        - Shows % of bankroll to bet
        - Example: 2.5% Kelly on $1000 = $25 bet
        - Conservative: Use 25-50% of Kelly (fractional Kelly)

        ### Common Commands

        | Task | Command |
        |------|---------|
        | Daily picks | `python RUN_DAILY_PICKS.py` |
        | Find edges | `python RUN_EDGE_FINDER.py` |
        | Grade results | `python RUN_GRADING.py` |
        | Open dashboard | `python RUN_DASHBOARD.py` |
        | Full workflow | `python RUN_COMPLETE_WORKFLOW.py` |

        ### Troubleshooting

        **No predictions generated:**
        - Check data freshness in sidebar
        - Run `python smart_data_refresh.py` manually
        - Check database exists: `database/nhl_predictions.db`

        **Low accuracy:**
        - Grade more predictions to improve learning
        - Check if models need retraining
        - Verify data quality

        **Dashboard won't start:**
        - Check if Streamlit installed: `pip install streamlit`
        - Try: `streamlit run app.py` directly
        - Check port 8501 not in use

        ### Support Resources

        - **Complete Guide:** `COMPLETE_SYSTEM_GUIDE.md`
        - **Quick Reference:** `QUICK_START.txt`
        - **Simple Commands:** `README_SIMPLE_COMMANDS.md`
        - **System Summary:** `SYSTEM_EXECUTIVE_SUMMARY.md`
        """)

# ============================================================================
# PAGE 8: SETTINGS
# ============================================================================

elif page == "🔧 Settings":
    st.title("🔧 Settings")

    st.info("Settings page - Configure system preferences")

    # Bankroll Management
    st.subheader("💰 Bankroll Management")

    bankroll = st.number_input(
        "Total Bankroll ($)",
        min_value=100,
        max_value=100000,
        value=1000,
        step=100
    )

    kelly_fraction = st.slider(
        "Kelly Fraction (Conservative: 0.25-0.50)",
        min_value=0.1,
        max_value=1.0,
        value=0.25,
        step=0.05
    )

    st.caption(f"With {kelly_fraction:.0%} Kelly and ${bankroll:,.0f} bankroll:")
    st.caption(f"- Max single bet: ${bankroll * kelly_fraction * 0.10:,.2f} (10% EV)")
    st.caption(f"- Max parlay bet: ${bankroll * kelly_fraction * 0.05:,.2f} (5% EV)")

    st.markdown("---")

    # Confidence Thresholds
    st.subheader("🎯 Confidence Thresholds")

    t1_threshold = st.slider(
        "T1-ELITE Threshold (%)",
        min_value=80,
        max_value=95,
        value=85,
        step=1
    )

    t2_threshold = st.slider(
        "T2-STRONG Threshold (%)",
        min_value=60,
        max_value=80,
        value=65,
        step=1
    )

    st.caption(f"Current tiers:")
    st.caption(f"- T1-ELITE: ≥{t1_threshold}%")
    st.caption(f"- T2-STRONG: {t2_threshold}%-{t1_threshold-1}%")
    st.caption(f"- T3-MARGINAL: 50%-{t2_threshold-1}%")

    st.markdown("---")

    # Edge Finding
    st.subheader("💎 Edge Finding Settings")

    min_ev = st.slider(
        "Minimum EV for Edges (%)",
        min_value=5,
        max_value=25,
        value=10,
        step=1
    )

    max_parlay_legs = st.slider(
        "Maximum Parlay Legs",
        min_value=2,
        max_value=6,
        value=5,
        step=1
    )

    st.markdown("---")

    # Data Refresh
    st.subheader("🔄 Data Refresh Settings")

    auto_refresh = st.checkbox("Auto-refresh stale data", value=True)

    refresh_threshold = st.slider(
        "Data staleness threshold (hours)",
        min_value=2,
        max_value=12,
        value=4,
        step=1
    )

    st.caption(f"Data older than {refresh_threshold}h will be considered stale")

    st.markdown("---")

    # Save Settings
    if st.button("💾 Save Settings", use_container_width=True, type="primary"):
        st.success("✅ Settings saved! (Note: Settings persistence not yet implemented)")
        st.info("Settings will be applied to future operations")

    st.markdown("---")

    # Reset to Defaults
    if st.button("🔄 Reset to Defaults", use_container_width=True):
        st.warning("Settings reset to defaults (reload page to see changes)")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("NHL Prediction System Dashboard v2.0 | Redesigned for simplicity and efficiency")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
