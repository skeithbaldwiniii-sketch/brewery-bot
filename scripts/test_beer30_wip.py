import os

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("BEER30_API_KEY")
BASE_URL = os.getenv(
    "BEER30_BASE_URL",
    "http://api.integration-demo.b30.app/",
).rstrip("/")


if not API_KEY:
    raise RuntimeError(
        "BEER30_API_KEY was not found in .env"
    )


START_DATE = "2026-08-01"
END_DATE = "2026-08-31"


endpoint = "reports/wip-report"

params = {
    "key": API_KEY,
    "date": END_DATE,
}


print("=" * 70)
print("BREWS SPRINGSTEIN - BEER30 WIP REPORT TEST")
print("=" * 70)
print()
print(f"Endpoint: {endpoint}")
print(f"Start date: {START_DATE}")
print(f"End date: {END_DATE}")
print()

try:
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params=params,
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")
    print(
        "Content-Type:",
        response.headers.get("Content-Type"),
    )
    print()

    if response.text:
        print(response.text[:20000])
    else:
        print("(No response body)")

except requests.RequestException as error:
    print(f"REQUEST ERROR: {error}")