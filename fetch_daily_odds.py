"""
Fetch Daily Game Odds
=====================

Simple script to fetch today's NHL game odds (moneylines, spreads, totals).
Designed to run once per day to stay well under 500 API calls/month limit.

Usage:
    python fetch_daily_odds.py

Author: NHL Prediction System
Date: 2025-10-30
"""

import logging
from datetime import datetime
from odds_api_integration import OddsAPIClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def fetch_daily_odds():
    """Fetch today's game odds"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("FETCH DAILY GAME ODDS")
    logger.info("=" * 80)
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    logger.info("")

    client = OddsAPIClient()

    # Check if API key is set
    if not client.api_key:
        logger.error("=" * 80)
        logger.error("NO API KEY FOUND")
        logger.error("=" * 80)
        logger.error("")
        logger.error("Set your API key:")
        logger.error("  PowerShell: [System.Environment]::SetEnvironmentVariable('ODDS_API_KEY', 'your_key', 'User')")
        logger.error("")
        logger.error("Then restart PowerShell and run this script again.")
        logger.error("=" * 80)
        client.close()
        return False

    # Show current API usage
    logger.info(f"API Usage: {client.requests_used_this_month}/500 calls used this month")
    logger.info(f"Remaining: {client.requests_remaining}/500")
    logger.info("")

    # Fetch game odds (ML, spreads, totals)
    logger.info("Fetching today's NHL game odds...")
    logger.info("  Markets: Moneylines, Spreads, Totals")
    logger.info("  Bookmakers: All US books")
    logger.info("")

    game_odds = client.fetch_game_odds(
        markets='h2h,spreads,totals',
        regions='us',
        force_refresh=True  # Always fetch fresh data
    )

    if game_odds.empty:
        logger.warning("No game odds fetched!")
        logger.warning("Possible reasons:")
        logger.warning("  - No NHL games today")
        logger.warning("  - Lines not posted yet")
        logger.warning("  - API issue")
        client.close()
        return False

    # Summary
    logger.info("=" * 80)
    logger.info("SUCCESS!")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"Fetched odds for {game_odds['game_id'].nunique()} games")
    logger.info(f"Total records: {len(game_odds)} (multiple bookmakers per game)")
    logger.info(f"API calls used: 1")
    logger.info(f"Remaining: {client.requests_remaining}/500")
    logger.info("")

    # Show sample games
    logger.info("Today's Games:")
    logger.info("-" * 80)

    for game_id in game_odds['game_id'].unique()[:5]:  # Show first 5 games
        game_data = game_odds[game_odds['game_id'] == game_id].iloc[0]
        away = game_data['away_team']
        home = game_data['home_team']

        logger.info(f"\n{away} @ {home}")

        # Show odds from each bookmaker
        game_odds_all = game_odds[game_odds['game_id'] == game_id]
        for _, odds in game_odds_all.head(3).iterrows():  # Show first 3 books
            ml_str = f"ML: {odds['away_ml']}/{odds['home_ml']}" if odds['away_ml'] else "ML: N/A"
            ou_str = f"O/U: {odds['over_under']}" if odds['over_under'] else "O/U: N/A"
            logger.info(f"  {odds['bookmaker']:15} {ml_str:20} {ou_str}")

    if game_odds['game_id'].nunique() > 5:
        logger.info(f"\n... and {game_odds['game_id'].nunique() - 5} more games")

    logger.info("")
    logger.info("-" * 80)
    logger.info("")
    logger.info("Odds saved to database: database/nhl_predictions.db")
    logger.info("Table: odds_api_game_odds")
    logger.info("")
    logger.info("These odds will be used by:")
    logger.info("  - TOI prediction system (game script analysis)")
    logger.info("  - Game importance calculator")
    logger.info("  - Your prediction models")
    logger.info("")
    logger.info("=" * 80)

    client.close()
    return True


if __name__ == "__main__":
    success = fetch_daily_odds()
    exit(0 if success else 1)
