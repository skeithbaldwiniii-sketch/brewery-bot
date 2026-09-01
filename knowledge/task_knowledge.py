import hashlib
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "task_knowledge.db"


DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "back",
    "be",
    "by",
    "do",
    "for",
    "from",
    "get",
    "in",
    "into",
    "is",
    "it",
    "leave",
    "make",
    "new",
    "next",
    "of",
    "off",
    "on",
    "or",
    "out",
    "replace",
    "remaining",
    "the",
    "this",
    "to",
    "update",
    "w",
    "wash",
    "with",
}


def connect_db():
    """Connect to the task knowledge database."""

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the task knowledge database."""

    connection = connect_db()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_text TEXT NOT NULL UNIQUE,
            normalized_task TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS task_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            component_type TEXT NOT NULL,
            component TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            UNIQUE(task_id, component_type, component)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS task_occurrences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            day_name TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            schedule_date TEXT,
            snapshot_id INTEGER,
            seen_at TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (snapshot_id) REFERENCES schedule_snapshots(id)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS task_terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            term TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            UNIQUE(task_id, term)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schedule_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_hash TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_task_terms_term
        ON task_terms(term)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_task_occurrences_day
        ON task_occurrences(day_name)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_task_occurrences_snapshot
        ON task_occurrences(snapshot_id)
        """
    )

    connection.commit()
    connection.close()


def normalize_task(task_text):
    """Normalize task text for searching."""

    text = task_text.lower().strip()

    text = re.sub(
        r"[^\w\s-]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def is_useful_word(word):
    """Determine whether a word is useful as a learned term."""

    if not word:
        return False

    if word in STOP_WORDS:
        return False

    # Ignore standalone numbers.
    if word.isdigit():
        return False

    # Ignore date-like values.
    if re.fullmatch(
        r"\d+[-_]\d+",
        word,
    ):
        return False

    if len(word) < 2:
        return False

    return True


def extract_terms(task_text):
    """
    Extract searchable terms from a task.

    The complete task text remains authoritative.
    These terms simply make searching easier.
    """

    normalized = normalize_task(task_text)

    words = normalized.split()

    terms = []

    useful_words = [
        word
        for word in words
        if is_useful_word(word)
    ]

    # Individual terms.
    for word in useful_words:

        if word not in terms:
            terms.append(word)

    # Two-word phrases.
    for index in range(len(words) - 1):

        first = words[index]
        second = words[index + 1]

        if not is_useful_word(first):
            continue

        if not is_useful_word(second):
            continue

        phrase = f"{first} {second}"

        if phrase not in terms:
            terms.append(phrase)

    return terms

def extract_task_components(task_text):
    """
    Extract likely actions and meaningful subjects from a task.

    This is intentionally generic. The brewery Board remains
    the source of truth; this function only identifies useful
    pieces of the task text for searching.

    Example:

        "keg off festbier (all halves)"

    becomes:

        action:
            keg

        subjects:
            festbier
    """

    normalized = normalize_task(task_text)

    # Remove parenthetical notes.
    normalized = re.sub(
        r"\([^)]*\)",
        " ",
        normalized,
    )

    # Normalize separators.
    normalized = normalized.replace("&", " ")
    normalized = normalized.replace("/", " ")

    words = normalized.split()

    if not words:
        return {
            "actions": [],
            "subjects": [],
        }

    # Generic operational verbs.
    #
    # These describe what is being done, not what the
    # brewery-specific object/product is.
    action_words = {
        "audit",
        "brew",
        "brewing",
        "can",
        "canning",
        "carb",
        "carbonating",
        "cip",
        "clean",
        "cleaning",
        "cull",
        "deliver",
        "delivery",
        "ferry",
        "flip",
        "inventory",
        "keg",
        "kegging",
        "make",
        "making",
        "mix",
        "pull",
        "release",
        "replace",
        "sani",
        "sanitize",
        "sanitizing",
        "stack",
        "tally",
        "transfer",
        "transferring",
        "update",
        "wash",
        "washing",
    }

    # Words that are useful grammatically but generally
    # aren't meaningful task subjects.
    ignored_words = {
        "a",
        "an",
        "all",
        "and",
        "at",
        "back",
        "by",
        "cases",
        "case",
        "for",
        "from",
        "in",
        "into",
        "of",
        "off",
        "halves",
        "on",
        "out",
        "remaining",
        "rest",
        "the",
        "to",
        "up",
        "w",
        "we",
        "with",
    }

    actions = []

    for word in words:

        if word in action_words and word not in actions:

            actions.append(word)

    subjects = []

    for word in words:

        if word in action_words:
            continue

        if word in ignored_words:
            continue

        # Ignore pure numbers.
        if word.isdigit():
            continue

        # Ignore very short fragments.
        if len(word) < 2:
            continue

        if word not in subjects:
            subjects.append(word)

    return {
        "actions": actions,
        "subjects": subjects,
    }

def create_schedule_fingerprint(schedule):
    """
    Create a deterministic fingerprint for the current schedule.

    If the exact schedule hasn't changed, the fingerprint will
    be identical.
    """

    normalized_schedule = {}

    for day in DAYS:

        normalized_schedule[day] = []

        for task in schedule.get(day, []):

            if isinstance(task, dict):

                normalized_schedule[day].append(
                    {
                        "task": task.get(
                            "task",
                            "",
                        ).strip(),
                        "completed": bool(
                            task.get(
                                "completed",
                                False,
                            )
                        ),
                    }
                )

            else:

                normalized_schedule[day].append(
                    {
                        "task": str(task).strip(),
                        "completed": False,
                    }
                )

    schedule_json = json.dumps(
        normalized_schedule,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        schedule_json.encode("utf-8")
    ).hexdigest()


def get_latest_snapshot():
    """Return the most recent schedule snapshot."""

    connection = connect_db()

    row = connection.execute(
        """
        SELECT
            id,
            snapshot_hash,
            created_at
        FROM schedule_snapshots
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    connection.close()

    if not row:
        return None

    return {
        "id": row[0],
        "snapshot_hash": row[1],
        "created_at": row[2],
    }


def create_snapshot(schedule):
    """
    Create a new schedule snapshot only if the schedule
    differs from the previous snapshot.

    Returns:

        {
            "id": snapshot ID,
            "created": True/False,
            "hash": fingerprint
        }
    """

    initialize_database()

    snapshot_hash = create_schedule_fingerprint(
        schedule
    )

    latest = get_latest_snapshot()

    if latest and latest["snapshot_hash"] == snapshot_hash:

        return {
            "id": latest["id"],
            "created": False,
            "hash": snapshot_hash,
        }

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    connection = connect_db()

    cursor = connection.execute(
        """
        INSERT INTO schedule_snapshots (
            snapshot_hash,
            created_at
        )
        VALUES (?, ?)
        """,
        (
            snapshot_hash,
            now,
        ),
    )

    snapshot_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "id": snapshot_id,
        "created": True,
        "hash": snapshot_hash,
    }


def learn_task(
    task_text,
    day_name,
    completed=False,
    schedule_date=None,
    snapshot_id=None,
):
    """
    Learn a task from the brewery schedule.

    The task itself is stored once.

    Schedule occurrences are associated with snapshots.
    """

    task_text = task_text.strip()

    if not task_text:
        return None

    day_name = day_name.lower().strip()

    if day_name not in DAYS:
        raise ValueError(
            f"Invalid day name: {day_name}"
        )

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    normalized = normalize_task(task_text)

    connection = connect_db()

    existing = connection.execute(
        """
        SELECT id
        FROM tasks
        WHERE task_text = ?
        """,
        (task_text,),
    ).fetchone()

    if existing:

        task_id = existing[0]

        connection.execute(
            """
            UPDATE tasks
            SET normalized_task = ?,
                last_seen = ?
            WHERE id = ?
            """,
            (
                normalized,
                now,
                task_id,
            ),
        )

    else:

        cursor = connection.execute(
            """
            INSERT INTO tasks (
                task_text,
                normalized_task,
                first_seen,
                last_seen
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                task_text,
                normalized,
                now,
                now,
            ),
        )

        task_id = cursor.lastrowid

    # Check whether this task already exists in
    # this exact snapshot/day.
    existing_occurrence = connection.execute(
        """
        SELECT id
        FROM task_occurrences
        WHERE task_id = ?
          AND day_name = ?
          AND (
                snapshot_id = ?
                OR (
                    snapshot_id IS NULL
                    AND ? IS NULL
                )
          )
        """,
        (
            task_id,
            day_name,
            snapshot_id,
            snapshot_id,
        ),
    ).fetchone()

    if existing_occurrence:

        connection.execute(
            """
            UPDATE task_occurrences
            SET completed = ?,
                schedule_date = ?,
                seen_at = ?
            WHERE id = ?
            """,
            (
                1 if completed else 0,
                schedule_date,
                now,
                existing_occurrence[0],
            ),
        )

    else:

        connection.execute(
            """
            INSERT INTO task_occurrences (
                task_id,
                day_name,
                completed,
                schedule_date,
                snapshot_id,
                seen_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                day_name,
                1 if completed else 0,
                schedule_date,
                snapshot_id,
                now,
            ),
        )

    # Learn searchable terms.
    terms = extract_terms(task_text)

    for term in terms:

        existing_term = connection.execute(
            """
            SELECT id
            FROM task_terms
            WHERE task_id = ?
              AND term = ?
            """,
            (
                task_id,
                term,
            ),
        ).fetchone()

        if existing_term:

            connection.execute(
                """
                UPDATE task_terms
                SET last_seen = ?
                WHERE id = ?
                """,
                (
                    now,
                    existing_term[0],
                ),
            )

        else:

            connection.execute(
                """
                INSERT INTO task_terms (
                    task_id,
                    term,
                    first_seen,
                    last_seen
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    task_id,
                    term,
                    now,
                    now,
                ),
            )

    connection.commit()
    connection.close()

    # Learn semantic components such as:
    #   keg → festbier
    #   release → festbier
    #   clean → tap lines
    learn_task_components(
        task_id,
        task_text,
    )

    return task_id

def sync_task_components():
    """
    Rebuild/synchronize learned task components for every
    task currently stored in the database.

    This is intentionally derived entirely from the
    existing task text. Nothing is hard-coded for
    individual brewery products.
    """

    connection = connect_db()

    rows = connection.execute(
        """
        SELECT id, task_text
        FROM tasks
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    learned = 0

    for row in rows:

        task_id = row[0]
        task_text = row[1]

        learn_task_components(
            task_id,
            task_text,
        )

        learned += 1

    return learned

def learn_task_components(task_id, task_text):
    """
    Learn action and subject components for a task.

    Components are metadata derived from the actual task
    text. They do not replace the original task.
    """

    components = extract_task_components(task_text)

    now = datetime.now().isoformat(timespec="seconds")

    conn = connect_db()

    try:
        cursor = conn.cursor()

        for action in components["actions"]:

            cursor.execute(
                """
                INSERT INTO task_components (
                    task_id,
                    component_type,
                    component,
                    first_seen,
                    last_seen
                )
                VALUES (?, ?, ?, ?, ?)

                ON CONFLICT(
                    task_id,
                    component_type,
                    component
                )
                DO UPDATE SET
                    last_seen = excluded.last_seen
                """,
                (
                    task_id,
                    "action",
                    action,
                    now,
                    now,
                ),
            )

        for subject in components["subjects"]:

            cursor.execute(
                """
                INSERT INTO task_components (
                    task_id,
                    component_type,
                    component,
                    first_seen,
                    last_seen
                )
                VALUES (?, ?, ?, ?, ?)

                ON CONFLICT(
                    task_id,
                    component_type,
                    component
                )
                DO UPDATE SET
                    last_seen = excluded.last_seen
                """,
                (
                    task_id,
                    "subject",
                    subject,
                    now,
                    now,
                ),
            )

        conn.commit()

    finally:
        conn.close()

def learn_schedule(
    schedule_by_day,
    schedule_date=None,
):
    """
    Learn an entire weekly schedule.

    A new snapshot is created only when the schedule
    has changed since the previous snapshot.
    """

    initialize_database()

    snapshot = create_snapshot(
        schedule_by_day
    )

    snapshot_id = snapshot["id"]

    learned = 0

    for day_name, tasks in schedule_by_day.items():

        for task in tasks:

            if isinstance(task, dict):

                task_text = task.get(
                    "task",
                    "",
                )

                completed = task.get(
                    "completed",
                    False,
                )

            else:

                task_text = str(task)
                completed = False

            if not task_text:
                continue

            learn_task(
                task_text=task_text,
                day_name=day_name,
                completed=completed,
                schedule_date=schedule_date,
                snapshot_id=snapshot_id,
            )

            learned += 1

    return {
        "entries": learned,
        "snapshot_id": snapshot_id,
        "new_snapshot": snapshot["created"],
        "snapshot_hash": snapshot["hash"],
    }


def find_tasks(search_term):
    """
    Search learned task knowledge.

    Searches complete task text and learned terms.
    """

    search_term = normalize_task(
        search_term
    )

    if not search_term:
        return []

    connection = connect_db()

    rows = connection.execute(
        """
        SELECT DISTINCT
            t.id,
            t.task_text,
            t.first_seen,
            t.last_seen
        FROM tasks t
        LEFT JOIN task_terms tt
            ON tt.task_id = t.id
        WHERE
            t.normalized_task LIKE ?
            OR tt.term LIKE ?
        ORDER BY t.task_text
        """,
        (
            f"%{search_term}%",
            f"%{search_term}%",
        ),
    ).fetchall()

    results = []

    for row in rows:

        task_id = row[0]

        day_rows = connection.execute(
            """
            SELECT DISTINCT day_name
            FROM task_occurrences
            WHERE task_id = ?
            ORDER BY
                CASE day_name
                    WHEN 'monday' THEN 1
                    WHEN 'tuesday' THEN 2
                    WHEN 'wednesday' THEN 3
                    WHEN 'thursday' THEN 4
                    WHEN 'friday' THEN 5
                    WHEN 'saturday' THEN 6
                    WHEN 'sunday' THEN 7
                END
            """,
            (task_id,),
        ).fetchall()

        results.append(
            {
                "task": row[1],
                "first_seen": row[2],
                "last_seen": row[3],
                "days": [
                    day[0]
                    for day in day_rows
                ],
            }
        )

    connection.close()

    return results

def find_tasks_by_component(
    subject=None,
    action=None,
):
    """
    Find learned tasks using semantic components.

    Examples:

        find_tasks_by_component(subject="festbier")

        find_tasks_by_component(
            subject="festbier",
            action="keg",
        )

    Returns the original task text and its scheduled days.
    """

    subject = (
        normalize_task(subject)
        if subject
        else None
    )

    action = (
        normalize_task(action)
        if action
        else None
    )

    if not subject and not action:
        return []

    connection = connect_db()

    query = """
        SELECT DISTINCT
            t.id,
            t.task_text,
            t.first_seen,
            t.last_seen
        FROM tasks t
        JOIN task_components tc
            ON tc.task_id = t.id
        WHERE 1 = 1
    """

    params = []

    if subject:
        query += """
            AND EXISTS (
                SELECT 1
                FROM task_components sc
                WHERE sc.task_id = t.id
                  AND sc.component_type = 'subject'
                  AND sc.component LIKE ?
            )
        """

        params.append(f"%{subject}%")

    if action:
        query += """
            AND EXISTS (
                SELECT 1
                FROM task_components ac
                WHERE ac.task_id = t.id
                  AND ac.component_type = 'action'
                  AND ac.component LIKE ?
            )
        """

        params.append(f"%{action}%")

    query += """
        ORDER BY t.task_text
    """

    rows = connection.execute(
        query,
        params,
    ).fetchall()

    results = []

    for row in rows:

        task_id = row[0]

        day_rows = connection.execute(
            """
            SELECT DISTINCT day_name
            FROM task_occurrences
            WHERE task_id = ?
            ORDER BY
                CASE day_name
                    WHEN 'monday' THEN 1
                    WHEN 'tuesday' THEN 2
                    WHEN 'wednesday' THEN 3
                    WHEN 'thursday' THEN 4
                    WHEN 'friday' THEN 5
                    WHEN 'saturday' THEN 6
                    WHEN 'sunday' THEN 7
                END
            """,
            (task_id,),
        ).fetchall()

        results.append(
            {
                "task": row[1],
                "first_seen": row[2],
                "last_seen": row[3],
                "days": [
                    day[0]
                    for day in day_rows
                ],
            }
        )

    connection.close()

    return results

def get_known_terms():
    """Return learned terms."""

    connection = connect_db()

    rows = connection.execute(
        """
        SELECT
            term,
            COUNT(*) AS task_count
        FROM task_terms
        GROUP BY term
        ORDER BY task_count DESC, term
        """
    ).fetchall()

    connection.close()

    return rows


def get_snapshot_history():
    """Return all known schedule snapshots."""

    connection = connect_db()

    rows = connection.execute(
        """
        SELECT
            id,
            snapshot_hash,
            created_at
        FROM schedule_snapshots
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "hash": row[1],
            "created_at": row[2],
        }
        for row in rows
    ]


if __name__ == "__main__":

    initialize_database()

    print(
        "Task knowledge database initialized successfully."
    )

    print(f"Database: {DB_PATH}")