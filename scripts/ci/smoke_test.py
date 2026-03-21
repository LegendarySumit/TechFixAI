import os
import sys
import requests


def check(url: str, expected_codes: set[int], timeout: int = 12) -> None:
    resp = requests.get(url, timeout=timeout, allow_redirects=False)
    if resp.status_code not in expected_codes:
        raise RuntimeError(f"{url} returned {resp.status_code}, expected one of {sorted(expected_codes)}")


def main() -> int:
    base_url = os.getenv("BASE_URL", "").strip().rstrip("/")
    if not base_url:
        print("BASE_URL is required")
        return 2

    try:
        check(f"{base_url}/", {200, 301, 302, 307, 308})
        check(f"{base_url}/health", {200, 503})

        metrics_enabled = os.getenv("EXPECT_METRICS", "true").lower() == "true"
        if metrics_enabled:
            check(f"{base_url}/metrics", {200})

        login_resp = requests.get(f"{base_url}/login", timeout=12, allow_redirects=False)
        if login_resp.status_code != 200:
            raise RuntimeError(f"{base_url}/login returned {login_resp.status_code}, expected 200")

        request_id = login_resp.headers.get("X-Request-ID", "")
        if not request_id:
            raise RuntimeError("X-Request-ID header missing on /login")

        print("SMOKE_TEST=PASS")
        return 0
    except Exception as exc:
        print(f"SMOKE_TEST=FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
