import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.schedule_writer import remove_task_from_day


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN — REMOVE SCHEDULE TEST")
    print("=" * 70)

    result = remove_task_from_day(
        "TEST - Canning Hacienda",
        "thursday",
    )

    print()

    if result["removed"]:
        print("TEST TASK REMOVED")
        print("-" * 70)
        print(f"Task: {result['task']}")
        print(f"Day:  {result['day']}")
        print(f"Row:  {result['row']}")
    else:
        print("TEST TASK NOT FOUND")

    print("-" * 70)


if __name__ == "__main__":
    main()