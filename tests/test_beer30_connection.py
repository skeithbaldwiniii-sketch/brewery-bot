import json
import os

import requests
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("BEER30_API_KEY")
base_url = os.getenv(
    "BEER30_BASE_URL",
    "http://api.integration-demo.b30.app/",
)


if not api_key:
    raise RuntimeError(
        "BEER30_API_KEY was not found in .env"
    )


response = requests.get(
    base_url,
    params={"key": api_key},
    timeout=30,
)

response.raise_for_status()

data = response.json()

print("BEER30 SANDBOX CONNECTION TEST")
print("-" * 40)
print(f"HTTP Status: {response.status_code}")
print(f"API endpoints discovered: {len(data.get('api', []))}")
print()

for endpoint in data.get("api", []):
    print(endpoint)

with open(
    "data/beer30_api_catalog.json",
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        data,
        file,
        indent=4,
    )

print()
print("API catalog saved to:")
print("data/beer30_api_catalog.json")
