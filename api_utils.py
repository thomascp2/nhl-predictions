"""
API utilities with retry logic and rate limiting

Usage:
    from api_utils import fetch_with_retry

    response = fetch_with_retry("https://api.example.com/data")
    data = response.json()
"""

import requests
import time
from typing import Optional
from system_logger import get_logger

logger = get_logger(__name__)


def fetch_with_retry(
    url: str,
    method: str = "GET",
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    json_data: Optional[dict] = None,
    max_retries: int = 3,
    timeout: int = 30,
    backoff_factor: float = 2.0
) -> requests.Response:
    """
    Fetch data from API with exponential backoff retry logic

    Args:
        url: API endpoint URL
        method: HTTP method (GET, POST, etc.)
        headers: Request headers
        params: Query parameters
        json_data: JSON request body
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        backoff_factor: Multiplier for wait time between retries

    Returns:
        requests.Response object

    Raises:
        requests.HTTPError: If all retries fail
        requests.Timeout: If request times out after all retries

    Example:
        >>> response = fetch_with_retry("https://api.nhl.com/api/v1/teams")
        >>> data = response.json()
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1}/{max_retries}: {method} {url}")

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=timeout
            )

            # Raise for 4xx/5xx errors
            response.raise_for_status()

            logger.debug(f"Success: {method} {url} (Status: {response.status_code})")
            return response

        except requests.exceptions.HTTPError as e:
            last_exception = e
            status_code = e.response.status_code

            # Don't retry 4xx errors (client errors) except 429 (rate limit)
            if 400 <= status_code < 500 and status_code != 429:
                logger.error(f"Client error {status_code}: {url}")
                raise

            # Retry 5xx errors (server errors) and 429 (rate limit)
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                logger.warning(f"HTTP {status_code} error, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Max retries reached for {url}")
                raise

        except requests.exceptions.Timeout as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                logger.warning(f"Timeout, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Max retries reached (timeout) for {url}")
                raise

        except requests.exceptions.ConnectionError as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                logger.warning(f"Connection error, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Max retries reached (connection) for {url}")
                raise

        except Exception as e:
            # Unexpected error - don't retry
            logger.error(f"Unexpected error: {e}")
            raise

    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("API request failed with unknown error")


def rate_limited_request(
    url: str,
    calls_per_minute: int = 60,
    **kwargs
) -> requests.Response:
    """
    Make an API request with rate limiting

    Args:
        url: API endpoint URL
        calls_per_minute: Maximum calls per minute
        **kwargs: Additional arguments passed to fetch_with_retry

    Returns:
        requests.Response object

    Example:
        >>> # Limit to 10 calls per minute
        >>> response = rate_limited_request(
        ...     "https://api.example.com/data",
        ...     calls_per_minute=10
        ... )
    """
    # Calculate minimum delay between requests
    min_delay = 60.0 / calls_per_minute

    # Use a global last_call_time (in production, use a class or module-level dict)
    global _last_call_time
    if not hasattr(rate_limited_request, '_last_call_time'):
        _last_call_time = {}

    # Get last call time for this rate limit
    key = f"{calls_per_minute}"
    last_call = _last_call_time.get(key, 0)

    # Calculate time since last call
    time_since_last = time.time() - last_call

    # Wait if needed
    if time_since_last < min_delay:
        wait_time = min_delay - time_since_last
        logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
        time.sleep(wait_time)

    # Make request
    response = fetch_with_retry(url, **kwargs)

    # Update last call time
    _last_call_time[key] = time.time()

    return response


# Example usage and testing
if __name__ == "__main__":
    print("Testing API utilities...")
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
            print("  [PASS] 404 error raised correctly")
        else:
            print(f"  [FAIL] Wrong error: {e}")
    except Exception as e:
        print(f"  [FAIL] Unexpected error: {e}")

    print()

    # Test 3: Rate limiting
    print("[TEST 3] Rate limiting (2 requests, 2 calls/min)")
    start_time = time.time()
    try:
        # First request (immediate)
        response1 = rate_limited_request(
            "https://api.nhl.com/api/v1/teams",
            calls_per_minute=2,  # 1 call every 30 seconds
            timeout=15
        )
        print(f"  Request 1: {response1.status_code}")

        # Second request (should wait ~30 seconds)
        response2 = rate_limited_request(
            "https://api.nhl.com/api/v1/teams",
            calls_per_minute=2,
            timeout=15
        )
        print(f"  Request 2: {response2.status_code}")

        elapsed = time.time() - start_time
        print(f"  Total time: {elapsed:.1f}s")
        if elapsed >= 30:
            print("  [PASS] Rate limiting working")
        else:
            print("  [FAIL] Should have waited ~30s")
    except Exception as e:
        print(f"  [FAIL] {e}")

    print()
    print("="*60)
    print("API utilities ready!")
    print("="*60)
    print()
    print("Usage in your code:")
    print("  from api_utils import fetch_with_retry")
    print("  response = fetch_with_retry('https://api.example.com/data')")
    print("  data = response.json()")
