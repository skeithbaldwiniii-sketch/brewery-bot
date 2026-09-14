import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.upserve import download_latest_upserve_report


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN — UPSERVE DOWNLOAD TEST")
    print("=" * 70)

    file_path = download_latest_upserve_report()

    print()
    print(f"Downloaded report: {file_path}")
    print(f"File exists: {file_path.exists()}")
    print(f"File size: {file_path.stat().st_size:,} bytes")
    print("=" * 70)


if __name__ == "__main__":
    main()