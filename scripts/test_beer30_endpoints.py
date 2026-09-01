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


TESTS = [
    (
        "reports/production-volume-brewed",
        {
            "start-date": START_DATE,
            "end-date": END_DATE,
        },
    ),
    (
        "reports/production-volume-packaged",
        {
            "start-date": START_DATE,
            "end-date": END_DATE,
        },
    ),
    (
        "reports/transfer-history",
        {
            "start-date": START_DATE,
            "end-date": END_DATE,
        },
    ),
    (
        "inventory/items",
        {
            "type": "kegging",
        },
    ),
    (
        "inventory/items",
        {
            "type": "canning",
        },
    ),
]


for endpoint, parameters in TESTS:

    print()
    print("=" * 70)
    print(endpoint)
    print("=" * 70)

    params = {
        "key": API_KEY,
        **parameters,
    }

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
            print(response.text[:10000])
        else:
            print("(No response body)")

    except requests.RequestException as error:

        print(f"REQUEST ERROR: {error}")
