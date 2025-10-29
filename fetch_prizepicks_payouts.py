"""
Fetch PrizePicks payout structure
"""

import requests
import json

def fetch_payout_structure():
    """Try to fetch PrizePicks payout structure"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://app.prizepicks.com/',
        'Origin': 'https://app.prizepicks.com'
    }

    # Try different potential endpoints
    endpoints = [
        "https://api.prizepicks.com/config",
        "https://api.prizepicks.com/payouts",
        "https://api.prizepicks.com/leagues/8",  # NHL league
        "https://api.prizepicks.com/projection_types",
    ]

    print("Searching for payout information...")
    print()

    for endpoint in endpoints:
        try:
            print(f"Trying: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"  SUCCESS! Found data")
                print(f"  Keys: {list(data.keys())}")

                # Look for payout-related info
                payout_keys = []
                for key in data.keys():
                    if 'payout' in key.lower() or 'odds' in key.lower() or 'multiplier' in key.lower():
                        payout_keys.append(key)

                if payout_keys:
                    print(f"  Payout-related keys: {payout_keys}")
                    for pk in payout_keys:
                        print(f"  {pk}: {data[pk]}")

                print()
            else:
                print(f"  Status: {response.status_code}")

        except Exception as e:
            print(f"  Error: {e}")

    print()
    print("="*80)
    print("KNOWN PRIZEPICKS PAYOUT STRUCTURE (from documentation)")
    print("="*80)
    print()
    print("Standard Power Play (all standard picks):")
    print("  2-pick: 3x")
    print("  3-pick: 5x")
    print("  4-pick: 10x")
    print("  5-pick: 20x")
    print("  6-pick: 25x")
    print()
    print("Goblin Mode (easier lines, lower payouts):")
    print("  Typically 0.5x - 0.75x of standard payout")
    print()
    print("Demon Mode (harder lines, higher payouts):")
    print("  Typically 1.25x - 1.5x of standard payout")
    print()
    print("Flash Sales:")
    print("  Boosted multipliers for limited time (varies)")
    print()
    print("Note: Mixing odds_types results in weighted average payouts")
    print()


if __name__ == "__main__":
    fetch_payout_structure()
