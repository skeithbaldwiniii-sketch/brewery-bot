import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.schedule_writer import add_task_to_day


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN — SCHEDULE WRITE TEST")
    print("=" * 70)

    result = add_task_to_day(
        "TEST - Canning Hacienda",
        "thursday",
    )

    print()
    print("TASK ADDED")
    print("-" * 70)
    print(f"Task: {result['task']}")
    print(f"Day:  {result['day']}")
    print(f"Row:  {result['row']}")
    print("-" * 70)


if __name__ == "__main__":
    main()