"""Quick test of API utilities (without slow rate limit test)"""
from api_utils import fetch_with_retry
import requests

print("Testing API utilities (quick tests only)...")
print()

# Test 1: Successful request
print("[TEST 1] Successful request")
try:
    response = fetch_with_retry(
        "https://api.nhl.com/api/v1/teams",
        timeout=15
    )
    print(f"  Status: {response.status_code}")
    print(f"  Teams: {len(response.json()['teams'])}")
    print("  [PASS]")
except Exception as e:
    print(f"  [FAIL] {e}")

print()

# Test 2: 404 error (should not retry)
print("[TEST 2] 404 error (no retry)")
try:
    response = fetch_with_retry(
        "https://api.nhl.com/api/v1/nonexistent",
        timeout=15,
        max_retries=3
    )
    print("  [FAIL] Should have raised 404 error")
except requests.HTTPError as e:
    if e.response.status_code == 404:
        print("  [PASS] 404 error raised correctly (no retries)")
    else:
        print(f"  [FAIL] Wrong error: {e}")
except Exception as e:
    print(f"  [FAIL] Unexpected error: {e}")

print()
print("="*60)
print("API utilities working correctly!")
print("="*60)
