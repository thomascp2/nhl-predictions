"""
Bankroll Management System

Tracks bankroll, calculates bet sizes using Kelly Criterion,
and enforces risk limits to prevent overbetting.

Usage:
    from bankroll_manager import BankrollManager

    # Initialize with starting bankroll
    manager = BankrollManager(initial_bankroll=1000)

    # Get recommended bet size for an edge
    bet_size = manager.get_bet_size(
        probability=0.60,
        payout_multiplier=2.0,
        edge=0.10
    )

    # Record bet result
    manager.record_bet(bet_size, won=True, payout=50)

    # Check bankroll status
    print(manager.get_status())
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict
from system_logger import get_logger

logger = get_logger(__name__)

DB_PATH = "database/nhl_predictions.db"


class BankrollManager:
    """
    Manages betting bankroll with Kelly Criterion and risk limits

    Prevents overbetting by:
    1. Using fractional Kelly (25% of full Kelly by default)
    2. Enforcing maximum bet size (5% of bankroll by default)
    3. Tracking daily/weekly risk exposure
    4. Warning when approaching risk limits
    """

    def __init__(
        self,
        initial_bankroll: float = None,
        kelly_fraction: float = 0.25,
        max_bet_pct: float = 0.05,
        max_daily_risk_pct: float = 0.20,
        db_path: str = DB_PATH
    ):
        """
        Initialize bankroll manager

        Args:
            initial_bankroll: Starting bankroll (if None, loads from database)
            kelly_fraction: Fraction of Kelly to bet (0.25 = quarter Kelly)
            max_bet_pct: Maximum bet as % of bankroll (0.05 = 5%)
            max_daily_risk_pct: Maximum daily risk as % of bankroll (0.20 = 20%)
            db_path: Path to database
        """
        self.db_path = db_path
        self.kelly_fraction = kelly_fraction
        self.max_bet_pct = max_bet_pct
        self.max_daily_risk_pct = max_daily_risk_pct

        # Initialize database tables
        self._init_database()

        # Load or set initial bankroll
        if initial_bankroll is not None:
            self._set_bankroll(initial_bankroll)
            logger.info(f"Bankroll initialized: ${initial_bankroll:,.2f}")
        else:
            self.current_bankroll = self._load_bankroll()
            if self.current_bankroll == 0:
                logger.warning("No bankroll found. Set initial bankroll first.")
            else:
                logger.info(f"Bankroll loaded: ${self.current_bankroll:,.2f}")

    def _init_database(self):
        """Initialize bankroll tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Bankroll history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bankroll_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                bankroll REAL NOT NULL,
                change_amount REAL,
                change_pct REAL,
                reason TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Bet history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bet_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                bet_type TEXT NOT NULL,  -- 'single', 'parlay'
                bet_description TEXT,
                bet_amount REAL NOT NULL,
                probability REAL,
                payout_multiplier REAL,
                expected_value REAL,
                result TEXT,  -- 'won', 'lost', 'pending'
                payout REAL,
                profit REAL,
                bankroll_before REAL,
                bankroll_after REAL,
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def _load_bankroll(self) -> float:
        """Load current bankroll from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT bankroll FROM bankroll_history
            ORDER BY created_at DESC
            LIMIT 1
        """)

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else 0.0

    def _set_bankroll(self, amount: float):
        """Set bankroll amount"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get previous bankroll
        previous = self._load_bankroll()

        # Calculate change
        change_amount = amount - previous if previous > 0 else 0
        change_pct = (change_amount / previous * 100) if previous > 0 else 0

        # Record new bankroll
        cursor.execute("""
            INSERT INTO bankroll_history
            (date, bankroll, change_amount, change_pct, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime('%Y-%m-%d'),
            amount,
            change_amount,
            change_pct,
            "Manual update" if previous > 0 else "Initial bankroll",
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        self.current_bankroll = amount

    def get_kelly_bet_size(
        self,
        probability: float,
        payout_multiplier: float,
        edge: float
    ) -> float:
        """
        Calculate Kelly Criterion bet size

        Formula: Kelly % = (edge) / (payout - 1)

        For a 60% probability bet with 2x payout:
        - Edge = (0.60 × 2.0) - 1 = 0.20 (20% EV)
        - Kelly = 0.20 / (2.0 - 1) = 0.20 / 1 = 20% of bankroll
        - Fractional Kelly (0.25) = 5% of bankroll

        Args:
            probability: Win probability (0-1)
            payout_multiplier: Payout multiplier (e.g., 2.0 for 2x)
            edge: Expected value edge (e.g., 0.20 for 20% edge)

        Returns:
            Kelly bet size in dollars
        """
        if edge <= 0:
            return 0.0

        # Kelly formula: f = edge / (payout - 1)
        kelly_pct = edge / (payout_multiplier - 1)

        # Apply fractional Kelly (e.g., 1/4 Kelly for safety)
        fractional_kelly_pct = kelly_pct * self.kelly_fraction

        # Calculate bet size
        kelly_bet = self.current_bankroll * fractional_kelly_pct

        return kelly_bet

    def get_bet_size(
        self,
        probability: float,
        payout_multiplier: float,
        edge: float,
        enforce_limits: bool = True
    ) -> Dict:
        """
        Get recommended bet size with risk limits

        Args:
            probability: Win probability (0-1)
            payout_multiplier: Payout multiplier
            edge: Expected value edge
            enforce_limits: Apply maximum bet and daily risk limits

        Returns:
            Dictionary with:
                - recommended_bet: Recommended bet amount
                - kelly_bet: Full fractional Kelly bet
                - max_bet: Maximum allowed bet
                - daily_risk_used: Current daily risk exposure
                - daily_risk_remaining: Remaining daily risk budget
                - warnings: List of warning messages
        """
        warnings = []

        # Calculate Kelly bet
        kelly_bet = self.get_kelly_bet_size(probability, payout_multiplier, edge)

        # Calculate max bet (% of bankroll)
        max_bet = self.current_bankroll * self.max_bet_pct

        # Get daily risk used
        daily_risk_used = self.get_daily_risk_exposure()
        max_daily_risk = self.current_bankroll * self.max_daily_risk_pct
        daily_risk_remaining = max_daily_risk - daily_risk_used

        # Determine recommended bet
        if not enforce_limits:
            recommended_bet = kelly_bet
        else:
            # Apply bet size limit
            recommended_bet = min(kelly_bet, max_bet)

            if kelly_bet > max_bet:
                warnings.append(
                    f"Kelly bet (${kelly_bet:.2f}) exceeds max bet (${max_bet:.2f}). "
                    f"Capping at ${max_bet:.2f}."
                )

            # Apply daily risk limit
            if recommended_bet > daily_risk_remaining:
                recommended_bet = max(0, daily_risk_remaining)
                warnings.append(
                    f"Approaching daily risk limit. Only ${daily_risk_remaining:.2f} "
                    f"of ${max_daily_risk:.2f} remaining today."
                )

            # Warn if bet is large
            if recommended_bet / self.current_bankroll > 0.03:  # > 3% of bankroll
                warnings.append(
                    f"Large bet: ${recommended_bet:.2f} is "
                    f"{recommended_bet / self.current_bankroll * 100:.1f}% of bankroll."
                )

        return {
            'recommended_bet': recommended_bet,
            'kelly_bet': kelly_bet,
            'max_bet': max_bet,
            'daily_risk_used': daily_risk_used,
            'daily_risk_remaining': daily_risk_remaining,
            'warnings': warnings,
            'kelly_fraction': self.kelly_fraction,
            'current_bankroll': self.current_bankroll
        }

    def get_daily_risk_exposure(self) -> float:
        """Get total amount at risk today (pending bets)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')

        cursor.execute("""
            SELECT SUM(bet_amount) FROM bet_history
            WHERE date = ? AND result = 'pending'
        """, (today,))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result[0] else 0.0

    def record_bet(
        self,
        bet_amount: float,
        bet_type: str,
        bet_description: str,
        probability: float,
        payout_multiplier: float,
        expected_value: float,
        result: str = 'pending',
        payout: float = 0.0
    ):
        """
        Record a bet in the database

        Args:
            bet_amount: Amount bet
            bet_type: 'single' or 'parlay'
            bet_description: Description of the bet
            probability: Win probability
            payout_multiplier: Payout multiplier
            expected_value: Expected value
            result: 'pending', 'won', or 'lost'
            payout: Payout amount (if result is 'won')
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        profit = payout - bet_amount if result == 'won' else (-bet_amount if result == 'lost' else 0)
        bankroll_before = self.current_bankroll
        bankroll_after = self.current_bankroll + profit

        cursor.execute("""
            INSERT INTO bet_history
            (date, bet_type, bet_description, bet_amount, probability,
             payout_multiplier, expected_value, result, payout, profit,
             bankroll_before, bankroll_after, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime('%Y-%m-%d'),
            bet_type,
            bet_description,
            bet_amount,
            probability,
            payout_multiplier,
            expected_value,
            result,
            payout,
            profit,
            bankroll_before,
            bankroll_after,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        # Update current bankroll if bet is settled
        if result in ['won', 'lost']:
            self._set_bankroll(bankroll_after)
            logger.info(f"Bet recorded: {result.upper()} - Profit: ${profit:+.2f}")

    def get_status(self) -> Dict:
        """Get current bankroll status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get stats
        today = datetime.now().strftime('%Y-%m-%d')

        # Pending bets today
        cursor.execute("""
            SELECT COUNT(*), SUM(bet_amount)
            FROM bet_history
            WHERE date = ? AND result = 'pending'
        """, (today,))
        pending_result = cursor.fetchone()
        pending_bets = pending_result[0] if pending_result[0] else 0
        pending_amount = pending_result[1] if pending_result[1] else 0

        # Settled bets today
        cursor.execute("""
            SELECT
                SUM(CASE WHEN result = 'won' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'lost' THEN 1 ELSE 0 END) as losses,
                SUM(profit) as total_profit
            FROM bet_history
            WHERE date = ? AND result IN ('won', 'lost')
        """, (today,))
        settled_result = cursor.fetchone()
        wins = settled_result[0] if settled_result[0] else 0
        losses = settled_result[1] if settled_result[1] else 0
        daily_profit = settled_result[2] if settled_result[2] else 0

        # All-time stats
        cursor.execute("""
            SELECT
                COUNT(*) as total_bets,
                SUM(CASE WHEN result = 'won' THEN 1 ELSE 0 END) as total_wins,
                SUM(CASE WHEN result = 'lost' THEN 1 ELSE 0 END) as total_losses,
                SUM(profit) as total_profit
            FROM bet_history
            WHERE result IN ('won', 'lost')
        """)
        all_time = cursor.fetchone()

        conn.close()

        return {
            'current_bankroll': self.current_bankroll,
            'daily_profit': daily_profit,
            'pending_bets': pending_bets,
            'pending_amount': pending_amount,
            'today_wins': wins,
            'today_losses': losses,
            'all_time_bets': all_time[0] if all_time[0] else 0,
            'all_time_wins': all_time[1] if all_time[1] else 0,
            'all_time_losses': all_time[2] if all_time[2] else 0,
            'all_time_profit': all_time[3] if all_time[3] else 0,
            'win_rate': (all_time[1] / all_time[0] * 100) if all_time[0] > 0 else 0,
            'roi': (all_time[3] / self.current_bankroll * 100) if self.current_bankroll > 0 else 0
        }

    def print_status(self):
        """Print formatted bankroll status"""
        status = self.get_status()

        print("="*60)
        print("BANKROLL STATUS")
        print("="*60)
        print(f"Current Bankroll: ${status['current_bankroll']:,.2f}")
        print()
        print("TODAY:")
        print(f"  Profit/Loss: ${status['daily_profit']:+,.2f}")
        print(f"  Pending Bets: {status['pending_bets']} (${status['pending_amount']:,.2f} at risk)")
        print(f"  Settled: {status['today_wins']}W - {status['today_losses']}L")
        print()
        print("ALL-TIME:")
        print(f"  Total Bets: {status['all_time_bets']}")
        print(f"  Record: {status['all_time_wins']}W - {status['all_time_losses']}L")
        print(f"  Win Rate: {status['win_rate']:.1f}%")
        print(f"  Total Profit: ${status['all_time_profit']:+,.2f}")
        print(f"  ROI: {status['roi']:+.1f}%")
        print("="*60)


# Example usage
if __name__ == "__main__":
    print("Testing Bankroll Manager...")
    print()

    # Initialize with $1000 bankroll
    manager = BankrollManager(initial_bankroll=1000)

    # Get bet size for an edge
    print("[TEST 1] Get bet size for 60% probability, 2x payout, 20% EV")
    bet_info = manager.get_bet_size(
        probability=0.60,
        payout_multiplier=2.0,
        edge=0.20
    )

    print(f"  Kelly Bet: ${bet_info['kelly_bet']:.2f}")
    print(f"  Max Bet: ${bet_info['max_bet']:.2f}")
    print(f"  Recommended: ${bet_info['recommended_bet']:.2f}")
    if bet_info['warnings']:
        for warning in bet_info['warnings']:
            print(f"  WARNING: {warning}")

    print()

    # Record a winning bet
    print("[TEST 2] Record a $50 bet (won, $100 payout)")
    manager.record_bet(
        bet_amount=50,
        bet_type='single',
        bet_description='Dylan Larkin POINTS O0.5 [GOBLIN]',
        probability=0.95,
        payout_multiplier=1.44,
        expected_value=0.37,
        result='won',
        payout=100
    )

    print()

    # Print status
    manager.print_status()

    print()
    print("="*60)
    print("Bankroll manager ready!")
    print("="*60)
