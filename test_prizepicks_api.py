"""
Test script to see what the PrizePicks API actually returns
"""

import requests
import json

def test_prizepicks_api():
    """Fetch and display raw PrizePicks API response"""

    base_url = "https://api.prizepicks.com/projections"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://app.prizepicks.com/',
        'Origin': 'https://app.prizepicks.com'
    }

    params = {
        'league_id': 8,  # NHL
        'per_page': 10,  # Just get a few to examine
        'single_stat': 'true'
    }

    print("Fetching from PrizePicks API...")
    print()

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()

        data = response.json()

        # Pretty print first projection
        if 'data' in data and len(data['data']) > 0:
            print("="*80)
            print("SAMPLE PROJECTION DATA (First Entry)")
            print("="*80)
            print(json.dumps(data['data'][0], indent=2))
            print()

            print("="*80)
            print("ATTRIBUTES AVAILABLE:")
            print("="*80)
            attrs = data['data'][0].get('attributes', {})
            for key, value in attrs.items():
                print(f"  {key}: {value}")
            print()

            # Check if there's odds/payout info
            print("="*80)
            print("LOOKING FOR ODDS/PAYOUT FIELDS:")
            print("="*80)
            potential_odds_fields = ['odds', 'payout', 'multiplier', 'odds_type',
                                     'line_type', 'flash_sale_multiplier']
            for field in potential_odds_fields:
                if field in attrs:
                    print(f"  FOUND: {field} = {attrs[field]}")
            print()

        else:
            print("No projection data found")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_prizepicks_api()
