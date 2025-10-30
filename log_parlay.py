"""
Quick parlay observation logger

Makes it easy to log parlay payouts you observe on PrizePicks.
This builds training data for the odds reverse engineering system.

Usage:
    python log_parlay.py

Example session:
    Date: 2025-10-29
    Payout: 2.25
    Number of legs: 2

    Leg 1:
      Player: Auston Matthews
      Prop type: shots
      Line: 3.5

    Leg 2:
      Player: Kirill Marchenko
      Prop type: shots
      Line: 2.5

    [SUCCESS] Parlay logged!
"""

from prizepicks_odds_scraper import PrizePicksOddsDatabase
from datetime import datetime
import sys


def log_parlay_interactive():
    """Interactive parlay observation logger"""
    print()
    print("="*80)
    print("PRIZEPICKS PARLAY OBSERVATION LOGGER")
    print("="*80)
    print()
    print("This tool helps you log actual parlay payouts from PrizePicks.")
    print("The system will reverse engineer individual pick odds from your observations.")
    print()

    try:
        # Get date
        date_input = input("Date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not date_input:
            date = datetime.now().strftime('%Y-%m-%d')
            print(f"  Using today's date: {date}")
        else:
            date = date_input

        print()

        # Get payout
        payout_input = input("Actual payout multiplier (e.g., 2.25 for $1 wins $2.25): ").strip()
        payout = float(payout_input)

        print()

        # Get number of legs
        num_legs_input = input("Number of legs in parlay: ").strip()
        num_legs = int(num_legs_input)

        print()

        # Get picks
        picks = []

        for i in range(num_legs):
            print(f"Leg {i+1}:")
            player = input("  Player name: ").strip()

            # Normalize prop type
            prop = input("  Prop type (shots/points/goals/assists/blocks/hits): ").strip().lower()

            # Common abbreviations
            if prop in ['sog', 'shot']:
                prop = 'shots'
            elif prop in ['pts', 'point']:
                prop = 'points'
            elif prop in ['goal']:
                prop = 'goals'
            elif prop in ['assist']:
                prop = 'assists'
            elif prop in ['block']:
                prop = 'blocks'
            elif prop in ['hit']:
                prop = 'hits'

            line = float(input("  Line (e.g., 3.5): "))

            picks.append({
                'player_name': player,
                'prop_type': prop,
                'line': line
            })

            print()

        # Confirmation
        print("="*80)
        print("CONFIRM YOUR PARLAY:")
        print("="*80)
        print(f"Date: {date}")
        print(f"Payout: {payout}x")
        print(f"Legs: {num_legs}")
        print()
        for i, pick in enumerate(picks, 1):
            print(f"  {i}. {pick['player_name']} {pick['prop_type'].upper()} O{pick['line']}")
        print()

        confirm = input("Is this correct? (y/n): ").strip().lower()

        if confirm != 'y':
            print()
            print("[CANCELLED] Parlay not logged. Run script again to retry.")
            return

        # Log it
        print()
        print("Logging parlay observation...")

        db = PrizePicksOddsDatabase()
        db.add_parlay_observation(picks, payout, date)

        # Show learned odds
        print()
        print("="*80)
        print("LEARNED INDIVIDUAL ODDS:")
        print("="*80)

        for pick in picks:
            mult, conf = db.get_implied_odds(
                pick['player_name'],
                pick['prop_type'],
                pick['line'],
                date
            )
            print(f"{pick['player_name']} {pick['prop_type'].upper()} O{pick['line']}")
            print(f"  Implied multiplier: {mult:.2f}x")
            print(f"  Confidence: {conf:.1%}")
            print()

        db.close()

        print("="*80)
        print("[SUCCESS] Parlay logged successfully!")
        print("="*80)
        print()
        print("Keep logging more parlays to improve accuracy!")
        print("Goal: 50-100 observations for solid ML training data")
        print()

    except KeyboardInterrupt:
        print()
        print()
        print("[CANCELLED] Logging interrupted by user.")
        sys.exit(0)

    except ValueError as e:
        print()
        print(f"[ERROR] Invalid input: {e}")
        print("Please make sure to enter numbers for payout, legs, and line values.")
        sys.exit(1)

    except Exception as e:
        print()
        print(f"[ERROR] Failed to log parlay: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def log_parlay_quick(picks, payout, date=None):
    """
    Quick logging without interactive prompts.

    Example:
        picks = [
            {'player_name': 'Auston Matthews', 'prop_type': 'shots', 'line': 3.5},
            {'player_name': 'Kirill Marchenko', 'prop_type': 'shots', 'line': 2.5}
        ]
        log_parlay_quick(picks, 2.25)
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    db = PrizePicksOddsDatabase()
    db.add_parlay_observation(picks, payout, date)
    db.close()

    print(f"[SUCCESS] Logged {len(picks)}-leg parlay with {payout}x payout")


if __name__ == "__main__":
    log_parlay_interactive()
