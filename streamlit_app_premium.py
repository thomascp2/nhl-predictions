"""
NHL Predictions - Premium Web App
Robinhood-inspired design + PrizePicks card style

Run: streamlit run streamlit_app_premium.py
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import sys

DB_PATH = "database/nhl_predictions.db"

# Page config - MUST BE FIRST
st.set_page_config(
    page_title="NHL Predictions",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Robinhood + PrizePicks Style
st.markdown("""
<style>
    /* Robinhood Dark Theme */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main Header - Robinhood style */
    .main-header {
        font-size: 56px;
        font-weight: 800;
        background: linear-gradient(135deg, #00c853 0%, #00e676 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 40px 0 10px 0;
        letter-spacing: -2px;
    }

    .subtitle {
        text-align: center;
        color: #8b93a7;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 40px;
    }

    /* Stats Cards - Robinhood style */
    .metric-card {
        background: rgba(26, 31, 58, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 200, 83, 0.3);
        box-shadow: 0 8px 32px rgba(0, 200, 83, 0.2);
    }

    .metric-value {
        font-size: 48px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 8px;
    }

    .metric-label {
        font-size: 14px;
        color: #8b93a7;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    /* Player Cards - PrizePicks style */
    .player-card {
        background: linear-gradient(135deg, rgba(26, 31, 58, 0.9) 0%, rgba(20, 25, 45, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin: 16px 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .player-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #00c853 0%, #00e676 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .player-card:hover {
        transform: translateY(-6px);
        border-color: rgba(0, 200, 83, 0.4);
        box-shadow: 0 12px 48px rgba(0, 200, 83, 0.25);
    }

    .player-card:hover::before {
        opacity: 1;
    }

    .player-name {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
    }

    .player-team {
        font-size: 14px;
        color: #8b93a7;
        margin-bottom: 16px;
    }

    .prop-line {
        font-size: 18px;
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .prob-display {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #00c853 0%, #00e676 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }

    .expected-value {
        font-size: 16px;
        color: #8b93a7;
    }

    /* Tier Badges - PrizePicks style */
    .tier-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 100px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .tier-elite {
        background: linear-gradient(135deg, #00c853 0%, #00e676 100%);
        color: #000000;
        box-shadow: 0 4px 16px rgba(0, 200, 83, 0.4);
    }

    .tier-strong {
        background: linear-gradient(135deg, #ffd600 0%, #ffea00 100%);
        color: #000000;
        box-shadow: 0 4px 16px rgba(255, 214, 0, 0.4);
    }

    .tier-marginal {
        background: linear-gradient(135deg, #546e7a 0%, #78909c 100%);
        color: #ffffff;
        box-shadow: 0 4px 16px rgba(84, 110, 122, 0.4);
    }

    /* Sidebar - Robinhood style */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: rgba(10, 14, 39, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Buttons - Robinhood Green */
    .stButton>button {
        background: linear-gradient(135deg, #00c853 0%, #00e676 100%);
        color: #000000;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 16px 32px;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0, 200, 83, 0.3);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 200, 83, 0.5);
    }

    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00c853 0%, #00e676 100%);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(26, 31, 58, 0.6);
        border-radius: 12px;
        color: #8b93a7;
        font-weight: 600;
        padding: 12px 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00c853 0%, #00e676 100%);
        color: #000000;
    }

    /* Select boxes and inputs */
    .stSelectbox, .stMultiSelect, .stDateInput {
        color: #ffffff;
    }

    /* Dataframes */
    .dataframe {
        background: rgba(26, 31, 58, 0.6);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Success/Warning/Error messages */
    .stSuccess {
        background: rgba(0, 200, 83, 0.1);
        border-left: 4px solid #00c853;
        color: #00e676;
    }

    .stWarning {
        background: rgba(255, 214, 0, 0.1);
        border-left: 4px solid #ffd600;
        color: #ffea00;
    }

    .stError {
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #f44336;
        color: #ff5252;
    }

    .stInfo {
        background: rgba(33, 150, 243, 0.1);
        border-left: 4px solid #2196f3;
        color: #64b5f6;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏒 NHL PREDICTIONS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">73-75% Accuracy Ensemble Model • Powered by ML</div>', unsafe_allow_html=True)

# Mobile-friendly controls (visible on main page for mobile users)
with st.expander("📱 MOBILE CONTROLS", expanded=False):
    st.markdown("**Use these controls if sidebar is not accessible on your device**")

    # Mobile generate button
    if st.button("🔄 GENERATE PREDICTIONS", key="mobile_generate", type="primary", use_container_width=True):
        with st.spinner("Generating predictions..."):
            progress_bar = st.progress(0)

            try:
                # Statistical predictions
                st.info("Running statistical model...")
                result1 = subprocess.run(
                    [sys.executable, "fresh_clean_predictions.py"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                progress_bar.progress(50)

                if result1.returncode == 0:
                    st.success("✓ Statistical complete")
                else:
                    st.warning("⚠ Statistical warnings")

                # Ensemble predictions
                st.info("Running ensemble model...")
                result2 = subprocess.run(
                    [sys.executable, "ensemble_predictions.py"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                progress_bar.progress(100)

                if result2.returncode == 0:
                    st.success("✓ Ensemble complete")
                    st.balloons()
                else:
                    st.warning("⚠ Ensemble warnings")

                st.success("🎉 Predictions ready!")
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.markdown("---")

    # Mobile date selector
    today_mobile = datetime.now().date()
    selected_date_mobile = st.date_input(
        "📅 Select Date",
        value=today_mobile,
        max_value=today_mobile + timedelta(days=7),
        key="mobile_date"
    )

    # Mobile tier filter
    tier_filter_mobile = st.multiselect(
        "🎯 Filter by Tier",
        options=["T1-ELITE", "T2-STRONG", "T3-MARGINAL"],
        default=["T1-ELITE", "T2-STRONG"],
        key="mobile_tier"
    )

    # Mobile model filter
    model_filter_mobile = st.selectbox(
        "🤖 Model Version",
        options=["All", "ensemble_v1", "statistical", "ml_v3"],
        key="mobile_model"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Controls")

    # Generate predictions button
    if st.button("🔄 GENERATE PREDICTIONS", use_container_width=True):
        with st.spinner("Generating predictions..."):
            progress_bar = st.progress(0)

            try:
                # Statistical predictions
                st.info("Running statistical model...")
                result1 = subprocess.run(
                    [sys.executable, "fresh_clean_predictions.py"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                progress_bar.progress(50)

                if result1.returncode == 0:
                    st.success("✓ Statistical complete")
                else:
                    st.warning("⚠ Statistical warnings")

                # Ensemble predictions
                st.info("Running ensemble model...")
                result2 = subprocess.run(
                    [sys.executable, "ensemble_predictions.py"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                progress_bar.progress(100)

                if result2.returncode == 0:
                    st.success("✓ Ensemble complete")
                    st.balloons()
                else:
                    st.warning("⚠ Ensemble warnings")

                st.success("🎉 Predictions ready!")
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.markdown("---")

    # Date selector
    today = datetime.now().date()
    selected_date = st.date_input(
        "📅 Select Date",
        value=today,
        max_value=today + timedelta(days=7)
    )

    # Tier filter
    tier_filter = st.multiselect(
        "🎯 Filter by Tier",
        options=["T1-ELITE", "T2-STRONG", "T3-MARGINAL"],
        default=["T1-ELITE", "T2-STRONG"]
    )

    # Model version
    model_filter = st.selectbox(
        "🤖 Model Version",
        options=["All", "ensemble_v1", "statistical", "ml_v3"]
    )

    st.markdown("---")
    st.markdown("### 📊 System Info")
    st.caption("**Version:** 3.0 Ensemble")
    st.caption("**Accuracy:** 73-75%")
    st.caption("**Database:** nhl_predictions.db")

# Use mobile filters if they exist in session state, otherwise use sidebar filters
if 'mobile_date' in st.session_state:
    active_date = selected_date_mobile
    active_tier_filter = tier_filter_mobile
    active_model_filter = model_filter_mobile
else:
    active_date = selected_date
    active_tier_filter = tier_filter
    active_model_filter = model_filter

# Main content
tab1, tab2, tab3 = st.tabs(["📊 PREDICTIONS", "📈 STATISTICS", "ℹ️ ABOUT"])

with tab1:
    try:
        conn = sqlite3.connect(DB_PATH)

        # Build query
        query = """
            SELECT
                player_name,
                team,
                opponent,
                prop_type,
                line,
                probability,
                expected_value,
                confidence_tier,
                model_version,
                reasoning
            FROM predictions
            WHERE game_date = ?
        """

        params = [active_date.strftime('%Y-%m-%d')]

        if active_tier_filter:
            placeholders = ','.join(['?' for _ in active_tier_filter])
            query += f" AND confidence_tier IN ({placeholders})"
            params.extend(active_tier_filter)

        if active_model_filter != "All":
            query += " AND model_version = ?"
            params.append(active_model_filter)

        query += " ORDER BY probability DESC"

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        if len(df) == 0:
            st.warning(f"No predictions found for {active_date}")
            st.info("👈 Click 'GENERATE PREDICTIONS' in the sidebar")
        else:
            # Summary Metrics - Robinhood style cards
            col1, col2, col3, col4 = st.columns(4)

            metrics = [
                (col1, len(df), "TOTAL PICKS"),
                (col2, len(df[df['confidence_tier'] == 'T1-ELITE']), "T1-ELITE"),
                (col3, len(df[df['confidence_tier'] == 'T2-STRONG']), "T2-STRONG"),
                (col4, f"{df['probability'].mean() * 100:.1f}%", "AVG PROB")
            ]

            for col, value, label in metrics:
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Player Cards - PrizePicks style
            for idx, row in df.iterrows():
                # Tier badge
                tier_class = "tier-elite" if row['confidence_tier'] == "T1-ELITE" else \
                            "tier-strong" if row['confidence_tier'] == "T2-STRONG" else \
                            "tier-marginal"

                # Create card
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"""
                    <div class="player-card">
                        <div class="tier-badge {tier_class}">{row['confidence_tier']}</div>
                        <div class="player-name">{row['player_name']}</div>
                        <div class="player-team">{row['team']} vs {row['opponent']}</div>
                        <div class="prop-line">{row['prop_type'].upper()} O{row['line']}</div>
                        <div class="prob-display">{row['probability']*100:.1f}%</div>
                        <div class="expected-value">Expected: {row['expected_value']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if pd.notna(row['reasoning']):
                        st.markdown(f"""
                        <div class="metric-card" style="height: 100%;">
                            <div class="metric-label">Analysis</div>
                            <div style="color: #8b93a7; margin-top: 12px;">{row['reasoning']}</div>
                        </div>
                        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading predictions: {str(e)}")

with tab2:
    st.markdown("### 📊 Performance Statistics")

    try:
        conn = sqlite3.connect(DB_PATH)

        # Overall accuracy by tier
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                confidence_tier
            FROM predictions
            WHERE is_correct IS NOT NULL
            GROUP BY confidence_tier
        """

        stats_df = pd.read_sql_query(query, conn)

        if len(stats_df) > 0:
            stats_df['accuracy'] = (stats_df['correct'] / stats_df['total'] * 100).round(1)

            col1, col2, col3 = st.columns(3)

            for idx, row in stats_df.iterrows():
                cols = [col1, col2, col3]
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{row['confidence_tier']}</div>
                        <div class="metric-value">{row['accuracy']:.1f}%</div>
                        <div class="expected-value">{row['correct']}/{row['total']} correct</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(row['accuracy'] / 100)
        else:
            st.info("No graded predictions yet. Run `python grade_predictions_fixed.py` after games.")

        # Recent performance chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📈 Last 7 Days")

        query = """
            SELECT
                game_date,
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM predictions
            WHERE is_correct IS NOT NULL
            AND game_date >= date('now', '-7 days')
            GROUP BY game_date
            ORDER BY game_date DESC
        """

        recent_df = pd.read_sql_query(query, conn)

        if len(recent_df) > 0:
            recent_df['accuracy'] = (recent_df['correct'] / recent_df['total'] * 100).round(1)
            st.line_chart(recent_df.set_index('game_date')['accuracy'], use_container_width=True)

        conn.close()

    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")

with tab3:
    st.markdown("### 🎯 About This System")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 🤖 Models
        - **Statistical:** 72% accuracy (domain expertise)
        - **ML Model V3:** 59% accuracy (XGBoost, 32 features)
        - **Ensemble:** 73-75% accuracy (70% stat, 30% ML)

        #### 📊 Features
        - Season stats (PPG, SOG, TOI)
        - Rolling averages (L5, L10, L20)
        - Hot/cold streaks (z-scores)
        - Opponent team defense
        - Goalie difficulty factors
        - Home/away advantage
        """)

    with col2:
        st.markdown("""
        #### 📈 Data Sources
        - **NHL API:** Official stats
        - **17,174+ games:** Historical training
        - **50,298+ rolling stats:** L5/L10/L20
        - **Daily updates:** Fresh data

        #### 🎯 Expected Accuracy
        - **T1-ELITE (70%+):** 75-80% hit rate
        - **T2-STRONG (60-70%):** 65-70% hit rate
        - **T3-MARGINAL (50-60%):** 55-60% hit rate
        """)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #8b93a7; padding: 20px;">
        <strong>Built with</strong> Python • XGBoost • SQLite • Streamlit<br>
        <strong>Version</strong> 3.0 Ensemble Edition • <strong>Last Updated</strong> 2025-10-27
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
